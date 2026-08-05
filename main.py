#!/usr/bin/env python3
"""
ATS Resume Analyzer - Telegram Chatbot
Complete production-ready solution using Groq API
"""

import logging
import html
import json
import os
import re
from pathlib import Path
from difflib import SequenceMatcher
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)

from database import Database
from document_parser import DocumentParser
from llm_engine import LLMEngine
from config import Config

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
config = Config()
db = Database()
parser = DocumentParser()
llm = LLMEngine()

# Conversation states
UPLOAD_JD, UPLOAD_RESUMES, ANALYZE_MODE, QUERY_MODE = range(4)

class ATS_Bot:
    def __init__(self):
        self.config = config
        self.db = db
        self.parser = parser
        self.llm = llm
        self.current_jd_text = None
        self.current_resumes = {}
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_message = """
🤖 *ATS Resume Analyzer Bot* 

I help you analyze resumes against job descriptions using AI.

*Available Commands:*
/upload_jd - Upload Job Description
/upload_resumes - Upload Resumes (multiple files)
/analyze - Analyze resumes vs JD
/improvements - Get improvement suggestions
/compare - Compare resumes
/extract - Extract information from resumes
/duplicates - Detect duplicate or near-duplicate resumes
/status - View current data status
/clear - Clear all data
/help - Show help menu

Start by uploading a JD and resumes! 📄
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📖 *How to Use ATS Bot:*

*Step 1: Upload Job Description*
/upload_jd - Upload a JD (PDF or DOCX)

*Step 2: Upload Resumes*
/upload_resumes - Upload multiple resumes at once

*Step 3: Get Analysis*
/analyze - Get AI analysis of all resumes
/compare - Compare resumes and rank them
/improvements - Get specific improvement suggestions
/extract - Extract key info from resumes
/duplicates - Detect duplicate or near-duplicate resumes

*Other Commands:*
/status - See what data you have uploaded
/clear - Clear all data and start fresh

*Supported Formats:*
✅ PDF (.pdf)
✅ DOCX (.docx)
✅ Text (.txt)

*Tips:*
- Upload JD first for better context
- You can upload multiple resumes at once
- AI provides detailed analysis and suggestions
- All processing happens locally (no external links)
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def upload_jd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start JD upload process"""
        logger.info("JD upload flow started by user %s", update.effective_user.id if update.effective_user else "unknown")
        await update.message.reply_text(
            "📄 Please upload the Job Description (PDF, DOCX, or TXT file)"
        )
        return UPLOAD_JD
    
    async def handle_jd_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle JD file upload"""
        if not update.message.document:
            await update.message.reply_text("❌ Please upload a file!")
            return UPLOAD_JD

        file_path = None
        
        try:
            file = update.message.document
            file_name = file.file_name
            
            # Download file
            file_obj = await update.message.effective_attachment.get_file()
            file_path = f"temp_{file_name}"
            await file_obj.download_to_drive(file_path)
            
            # Parse document
            parsed = self.parser.parse_document(file_path)
            jd_text = parsed.get('text', '')
            if not jd_text:
                await update.message.reply_text(
                    "⚠️ JD uploaded, but I could not extract any text from the file. If this is a scanned PDF, please upload a text-based PDF, DOCX, or TXT file."
                )
                return UPLOAD_JD
            self.current_jd_text = jd_text
            
            # Store in database
            saved = self.db.save_jd(jd_text, file_name)
            if not saved:
                await update.message.reply_text(
                    "❌ I received the JD, but I could not save it to the database. Please try again."
                )
                return UPLOAD_JD
            
            await update.message.reply_text(
                f"✅ JD uploaded successfully!\n\n📊 File: {file_name}\n📝 Characters: {len(jd_text)}\n\nNow upload resumes using /upload_resumes"
            )
            return ConversationHandler.END
            
        except Exception as e:
            logger.exception("Error uploading JD")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return UPLOAD_JD
        finally:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
            except Exception:
                logger.exception("Failed to clean up temporary JD file")
    
    async def upload_resumes_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start resume upload process"""
        await update.message.reply_text(
            "📄 Please upload resumes (you can upload multiple files one by one)\n\nSend /done when finished uploading"
        )
        context.user_data['resumes'] = {}
        return UPLOAD_RESUMES
    
    async def handle_resume_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle resume file uploads"""
        if update.message.text and update.message.text.lower() == '/done':
            if not context.user_data.get('resumes'):
                await update.message.reply_text("❌ Please upload at least one resume!")
                return UPLOAD_RESUMES
            
            # Save to database
            for name, payload in context.user_data['resumes'].items():
                self.db.save_resume(
                    payload.get('text', ''),
                    name,
                    image_count=payload.get('image_count', 0),
                    image_details=payload.get('image_details', ''),
                    image_paths=json.dumps(payload.get('image_paths', []))
                )
            
            self.current_resumes = self.db.get_all_resumes()
            
            await update.message.reply_text(
                f"✅ Resumes saved! {len(context.user_data['resumes'])} new file(s) stored.\n\nNow use:\n/analyze - Get AI analysis\n/improvements - Get suggestions\n/compare - Compare resumes"
            )
            return ConversationHandler.END
        
        if not update.message.document:
            await update.message.reply_text("Please upload a file or type /done to finish")
            return UPLOAD_RESUMES
        
        try:
            file = update.message.document
            file_name = file.file_name
            
            # Download file
            file_obj = await update.message.effective_attachment.get_file()
            file_path = f"temp_{file_name}"
            await file_obj.download_to_drive(file_path)
            
            # Parse document
            parsed = self.parser.parse_document(file_path)
            resume_text = parsed.get('text', '')
            image_count = parsed.get('image_count', 0)
            image_details = parsed.get('image_details', '')
            extracted_images = parsed.get('images', [])

            if not resume_text and image_count == 0:
                await update.message.reply_text(
                    f"⚠️ Resume '{file_name}' uploaded, but I could not extract any text or detect any embedded images. Please send a text-based PDF, DOCX, or TXT file."
                )
                if os.path.exists(file_path):
                    os.remove(file_path)
                return UPLOAD_RESUMES

            existing_resumes = self.db.get_all_resumes()
            duplicate_with_existing = self._find_duplicate_resume(resume_text, existing_resumes)
            duplicate_with_batch = self._find_duplicate_resume(resume_text, context.user_data.get('resumes', {}))

            if duplicate_with_existing:
                duplicate_name, similarity = duplicate_with_existing
                await update.message.reply_text(
                    f"⚠️ Resume '{file_name}' appears to be a duplicate of an already stored resume '{duplicate_name}' ({round(similarity * 100)}% similar). I kept the original and skipped this duplicate."
                )
                if os.path.exists(file_path):
                    os.remove(file_path)
                return UPLOAD_RESUMES

            if duplicate_with_batch:
                duplicate_name, similarity = duplicate_with_batch
                await update.message.reply_text(
                    f"⚠️ Resume '{file_name}' appears to be a duplicate of another uploaded resume '{duplicate_name}' ({round(similarity * 100)}% similar). I kept the first version and skipped this duplicate."
                )
                if os.path.exists(file_path):
                    os.remove(file_path)
                return UPLOAD_RESUMES

            image_paths = []
            if extracted_images:
                os.makedirs(Config.IMAGE_DIR, exist_ok=True)
                for index, image in enumerate(extracted_images, start=1):
                    image_name = f"{Path(file_name).stem}_{index}.{image['format']}"
                    image_path = os.path.join(Config.IMAGE_DIR, image_name)
                    with open(image_path, 'wb') as image_file:
                        image_file.write(image['data'])
                    image_paths.append(image_path)

            context.user_data.setdefault('resumes', {})[file_name] = {
                'text': resume_text,
                'image_count': image_count,
                'image_details': image_details,
                'image_paths': image_paths
            }
            
            # Cleanup
            if os.path.exists(file_path):
                os.remove(file_path)
            
            resume_count = len(context.user_data['resumes'])
            await update.message.reply_text(
                f"✅ Resume '{file_name}' uploaded! ({resume_count} total new file(s))\n\nUpload more or type /done"
            )
            return UPLOAD_RESUMES
            
        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
            return UPLOAD_RESUMES
    
    async def analyze_resumes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Analyze all resumes against JD"""
        try:
            # Check if data exists
            jd_text = self.db.get_jd()
            resumes = self.db.get_all_resumes()
            
            if not jd_text:
                await update.message.reply_text("❌ Please upload a JD first using /upload_jd")
                return
            
            if not resumes:
                await update.message.reply_text("❌ Please upload resumes first using /upload_resumes")
                return
            
            await update.message.reply_text("🔍 Analyzing resumes... This may take a moment ⏳")
            
            # Generate analysis
            analysis = self.llm.analyze_resumes(jd_text, resumes)
            
            # Send analysis in chunks (Telegram message limit is 4096)
            for chunk in self._split_message(analysis, 4000):
                await update.message.reply_text(chunk)
            
        except Exception as e:
            logger.error(f"Error analyzing resumes: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def get_improvements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get improvement suggestions"""
        try:
            jd_text = self.db.get_jd()
            resumes = self.db.get_all_resumes()
            
            if not jd_text or not resumes:
                await update.message.reply_text("❌ Please upload JD and resumes first")
                return
            
            await update.message.reply_text("📝 Generating improvement suggestions... ⏳")
            
            improvements = self.llm.get_improvements(jd_text, resumes)
            
            for chunk in self._split_message(improvements, 4000):
                await update.message.reply_text(chunk)
            
        except Exception as e:
            logger.error(f"Error getting improvements: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def compare_resumes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Compare and rank resumes"""
        try:
            jd_text = self.db.get_jd()
            resumes = self.db.get_all_resumes()
            
            if not jd_text or not resumes:
                await update.message.reply_text("❌ Please upload JD and resumes first")
                return
            
            await update.message.reply_text("🔄 Comparing resumes... ⏳")
            
            comparison = self.llm.compare_resumes(jd_text, resumes)

            table_message = self._format_compare_table(comparison)
            if table_message:
                for chunk in self._split_message(table_message, 3500):
                    await update.message.reply_text(f"<pre>{html.escape(chunk)}</pre>", parse_mode='HTML')
            else:
                for chunk in self._split_message(comparison, 4000):
                    await update.message.reply_text(chunk)
            
        except Exception as e:
            logger.error(f"Error comparing resumes: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def extract_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Extract information from resumes"""
        try:
            resumes = self.db.get_all_resumes()
            
            if not resumes:
                await update.message.reply_text("❌ Please upload resumes first")
                return
            
            await update.message.reply_text("📊 Extracting information... ⏳")
            
            extracted = self.llm.extract_info(resumes)

            formatted_extract = self._format_extract_output(extracted)
            if formatted_extract:
                for chunk in self._split_message(formatted_extract, 3500):
                    await update.message.reply_text(chunk)
            else:
                for chunk in self._split_message(extracted, 4000):
                    await update.message.reply_text(chunk)
            
        except Exception as e:
            logger.error(f"Error extracting info: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def detect_duplicates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Detect near-duplicate or repeated resume submissions."""
        try:
            resumes = self.db.get_all_resumes()

            if len(resumes) < 2:
                await update.message.reply_text("❌ Upload at least two resumes to check for duplicates.")
                return

            report = self._format_duplicate_report(resumes)
            if report:
                await update.message.reply_text(report)
            else:
                await update.message.reply_text("✅ No near-duplicate resumes found.")
        except Exception as e:
            logger.error(f"Error detecting duplicates: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current data status"""
        try:
            jd_text = self.db.get_jd()
            resumes = self.db.get_all_resumes()
            jd_file = self.db.get_jd_filename()
            resume_files = self.db.get_resume_filenames()
            
            status_msg = "📊 Current Status:\n\n"
            
            if jd_text:
                status_msg += f"✅ JD: {jd_file}\n📝 {len(jd_text)} characters\n\n"
            else:
                status_msg += "❌ No JD uploaded\n\n"
            
            if resumes:
                status_msg += f"✅ Resumes: {len(resumes)} file(s)\n"
                resume_info = self.db.get_resume_info()
                for resume in resume_info:
                    detail = f"  📄 {resume['filename']}"
                    if resume['image_count']:
                        detail += f" — {resume['image_count']} image(s) detected"
                        if resume['image_details']:
                            detail += f" ({resume['image_details']})"
                    status_msg += detail + "\n"
            else:
                status_msg += "❌ No resumes uploaded\n"
            
            await update.message.reply_text(status_msg)
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def clear_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all data"""
        try:
            self.db.clear_all()
            self.current_jd_text = None
            self.current_resumes = {}
            await update.message.reply_text("🗑️ All data cleared! Start fresh with /upload_jd")
        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    async def handle_text_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle free-form text queries about resumes"""
        try:
            jd_text = self.db.get_jd()
            resumes = self.db.get_all_resumes()
            
            if not jd_text or not resumes:
                await update.message.reply_text("❌ Please upload JD and resumes first")
                return
            
            query = update.message.text
            await update.message.reply_text(f"🤔 Processing: '{query}'... ⏳")

            if self._is_image_query(query):
                image_entries = self.db.get_resume_images()
                if image_entries:
                    await update.message.reply_text("✅ I found resumes with images. Sending the image file(s) now...")
                    any_sent = False
                    for entry in image_entries:
                        resume_name = entry['filename']
                        for image_path in entry.get('image_paths', []):
                            if os.path.exists(image_path):
                                caption = f"Image from resume: {resume_name}"
                                try:
                                    await self._send_image_file(update, image_path, caption)
                                    any_sent = True
                                except Exception as send_exc:
                                    logger.warning(f"Failed to send image {image_path}: {send_exc}")
                                    continue
                    if not any_sent:
                        await update.message.reply_text("❌ I found images in the resumes, but I could not send the extracted image files. Please check the bot logs.")
                    return
                await update.message.reply_text("❌ No resume images found.")
                return
            
            # Generate custom response
            response = self.llm.custom_query(jd_text, resumes, query)
            
            for chunk in self._split_message(response, 4000):
                await update.message.reply_text(chunk)
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            await update.message.reply_text(f"❌ Error: {str(e)}")

    @staticmethod
    def _is_image_query(text: str) -> bool:
        """Detect when the user wants actual resume image files."""
        text = text or ""
        image_terms = r"\b(image|photo|picture|pic|profile picture)\b"
        action_terms = r"\b(send|show|display|any|only|found|find)\b"
        if re.search(image_terms, text, re.I) and re.search(action_terms, text, re.I):
            return True
        if re.search(r"\b(image only|photo only|picture only|send image|send photo)\b", text, re.I):
            return True
        return False

    async def _send_image_file(self, update: Update, image_path: str, caption: str):
        """Send an image file via Telegram, with fallback to document if needed."""
        if image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
            with open(image_path, 'rb') as img_file:
                await update.message.reply_photo(photo=img_file, caption=caption)
        else:
            with open(image_path, 'rb') as img_file:
                await update.message.reply_document(document=img_file, filename=os.path.basename(image_path))
    
    @staticmethod
    def _split_message(text: str, max_length: int = 4000) -> list:
        """Split message into chunks"""
        chunks = []
        current_chunk = ""
        
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 > max_length:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += '\n' + line if current_chunk else line
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks if chunks else ["No response generated"]

    @staticmethod
    def _format_compare_table(raw_response: str) -> str:
        """Turn JSON comparison output into a fixed-width table."""
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned

            payload = json.loads(cleaned)
            rows = payload.get("rows", [])
            summary = payload.get("summary", "")
            recommendation = payload.get("recommendation", "")

            headers = ["Rank", "Candidate", "Skill", "Exp", "Fit"]
            widths = [4, 22, 7, 7, 7]
            table_rows = []

            def _clip(value: object, limit: int) -> str:
                text = str(value or "")
                return text if len(text) <= limit else text[: max(0, limit - 3)] + "..."

            def _pad(value: object, width: int) -> str:
                return _clip(value, width).ljust(width)

            header_line = " | ".join(_pad(header, width) for header, width in zip(headers, widths))
            separator_line = "-+-".join("-" * width for width in widths)
            table_rows.append(header_line)
            table_rows.append(separator_line)

            for row in rows:
                table_rows.append(
                    " | ".join(
                        [
                            _pad(row.get("rank", ""), widths[0]),
                            _pad(row.get("candidate", ""), widths[1]),
                            _pad(row.get("skill_match", ""), widths[2]),
                            _pad(row.get("experience_match", ""), widths[3]),
                            _pad(row.get("overall_fit", ""), widths[4]),
                        ]
                    )
                )

            detail_rows = ["\nNotes:"]
            for row in rows:
                detail_rows.append(
                    f"{row.get('rank', '')}. {row.get('candidate', '')} - {row.get('notes', '')}"
                )

            output_parts = ["\n".join(table_rows), "\n".join(detail_rows)]
            if summary:
                output_parts.append(f"Summary: {summary}")
            if recommendation:
                output_parts.append(f"Recommendation: {recommendation}")

            return "\n\n".join(output_parts).strip()
        except Exception:
            return ""

    @staticmethod
    def _format_extract_output(raw_response: str) -> str:
        """Turn JSON extraction output into readable resume sections."""
        try:
            cleaned = raw_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                cleaned = cleaned.replace("json\n", "", 1) if cleaned.startswith("json\n") else cleaned

            payload = json.loads(cleaned)
            resumes = payload.get("resumes", [])
            if not resumes:
                return ""

            blocks = []
            for index, resume in enumerate(resumes, start=1):
                name = resume.get("name", f"Resume {index}")
                personal_info = resume.get("personal_info", {})
                skills = resume.get("skills", [])
                experience = resume.get("experience", [])
                education = resume.get("education", [])
                certifications = resume.get("certifications", [])
                languages = resume.get("languages", [])
                summary = resume.get("summary", "")

                block_lines = [
                    f"Resume {index}: {name}",
                    f"Name: {personal_info.get('name', 'N/A')}",
                    f"Email: {personal_info.get('email', 'N/A')}",
                    f"Phone: {personal_info.get('phone', 'N/A')}",
                    f"Location: {personal_info.get('location', 'N/A')}",
                    f"Summary: {summary or 'N/A'}",
                    f"Skills: {', '.join(skills) if skills else 'N/A'}",
                    f"Experience: {', '.join(experience) if experience else 'N/A'}",
                    f"Education: {', '.join(education) if education else 'N/A'}",
                    f"Certifications: {', '.join(certifications) if certifications else 'N/A'}",
                    f"Languages: {', '.join(languages) if languages else 'N/A'}",
                ]
                blocks.append("\n".join(block_lines))

            return "\n\n".join(blocks).strip()
        except Exception:
            return ""

    @staticmethod
    def _normalize_resume_text(text: str) -> str:
        """Normalize resume text for similarity comparison."""
        normalized = re.sub(r"[^a-z0-9]+", " ", text.lower())
        return re.sub(r"\s+", " ", normalized).strip()

    @classmethod
    def _resume_similarity(cls, first_text: str, second_text: str) -> float:
        """Compute a simple similarity score between two resumes."""
        first_normalized = cls._normalize_resume_text(first_text)
        second_normalized = cls._normalize_resume_text(second_text)

        if not first_normalized or not second_normalized:
            return 0.0

        sequence_score = SequenceMatcher(None, first_normalized, second_normalized).ratio()

        first_tokens = set(first_normalized.split())
        second_tokens = set(second_normalized.split())
        union = first_tokens | second_tokens
        jaccard_score = len(first_tokens & second_tokens) / len(union) if union else 0.0

        return round((sequence_score * 0.6) + (jaccard_score * 0.4), 3)

    @classmethod
    def _find_duplicate_pairs(cls, resumes: dict, threshold: float = 0.82) -> list:
        """Return resume pairs whose similarity exceeds the threshold."""
        resume_items = list(resumes.items())
        duplicate_pairs = []

        for left_index in range(len(resume_items)):
            left_name, left_text = resume_items[left_index]
            for right_index in range(left_index + 1, len(resume_items)):
                right_name, right_text = resume_items[right_index]
                similarity = cls._resume_similarity(left_text, right_text)
                if similarity >= threshold:
                    duplicate_pairs.append((left_name, right_name, similarity))

        duplicate_pairs.sort(key=lambda item: item[2], reverse=True)
        return duplicate_pairs

    @classmethod
    def _extract_resume_text(cls, resume_payload):
        """Extract plain text from a resume payload or string."""
        if isinstance(resume_payload, dict):
            return resume_payload.get('text', '')
        return resume_payload or ''

    @classmethod
    def _find_duplicate_resume(cls, resume_text: str, existing_resumes: dict, threshold: float = 0.82):
        """Return the first duplicate candidate for a resume, or None."""
        if not existing_resumes:
            return None

        best_match = None
        best_score = 0.0

        for filename, content in existing_resumes.items():
            existing_text = cls._extract_resume_text(content)
            similarity = cls._resume_similarity(resume_text, existing_text)
            if similarity >= threshold and similarity > best_score:
                best_score = similarity
                best_match = filename

        return (best_match, best_score) if best_match else None

    @classmethod
    def _format_duplicate_report(cls, resumes: dict) -> str:
        """Format duplicate detection results for chat."""
        duplicate_pairs = cls._find_duplicate_pairs(resumes)
        if not duplicate_pairs:
            return ""

        lines = ["⚠️ Similar resume submissions detected:", ""]
        for left_name, right_name, similarity in duplicate_pairs:
            lines.append(f"- {left_name} <-> {right_name}: {round(similarity * 100)}% similar")

        lines.append("")
        lines.append("Tip: Review these resumes manually to confirm whether they are near-identical or repeated uploads.")
        return "\n".join(lines)

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log unexpected handler errors and keep the bot running."""
        logger.exception("Unhandled exception while processing update")
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Something went wrong while processing that file. Please try again."
            )


def main():
    """Main bot function"""
    bot = ATS_Bot()
    
    # Create application
    app = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Conversation handler for JD upload
    jd_conv_handler = ConversationHandler(
        entry_points=[CommandHandler(['upload_jd', 'uploadjd'], bot.upload_jd_start)],
        states={
            UPLOAD_JD: [MessageHandler(filters.Document.ALL, bot.handle_jd_upload)],
        },
        fallbacks=[]
    )
    
    # Conversation handler for resume upload
    resume_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('upload_resumes', bot.upload_resumes_start)],
        states={
            UPLOAD_RESUMES: [
                MessageHandler(filters.Document.ALL, bot.handle_resume_upload),
                MessageHandler(filters.TEXT & filters.Regex(r'^/done'), bot.handle_resume_upload)
            ],
        },
        fallbacks=[]
    )
    
    # Add handlers
    app.add_handler(CommandHandler('start', bot.start))
    app.add_handler(CommandHandler('help', bot.help_command))
    app.add_handler(jd_conv_handler)
    app.add_handler(resume_conv_handler)
    app.add_handler(CommandHandler('analyze', bot.analyze_resumes))
    app.add_handler(CommandHandler('improvements', bot.get_improvements))
    app.add_handler(CommandHandler('compare', bot.compare_resumes))
    app.add_handler(CommandHandler('extract', bot.extract_info))
    app.add_handler(CommandHandler('duplicates', bot.detect_duplicates))
    app.add_handler(CommandHandler('status', bot.status))
    app.add_handler(CommandHandler('clear', bot.clear_data))
    app.add_error_handler(bot.error_handler)
    
    # Text handler for custom queries (must be last)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_text_query))
    
    # Start bot
    logger.info("Starting ATS Resume Analyzer Bot...")
    app.run_polling()


if __name__ == '__main__':
    main()
