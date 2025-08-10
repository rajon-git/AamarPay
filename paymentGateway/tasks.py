from celery import shared_task
from .models import FileUpload, ActivityLog
import os
from docx import Document

@shared_task(bind=True)
def process_file_wordcount(self, fileupload_id):
    try:
        file_obj = FileUpload.objects.get(pk=fileupload_id)
        file_path = file_obj.file.path
        ext = os.path.splitext(file_path)[1].lower()

        text = ""
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        elif ext == ".docx":
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs]
            text = "\n".join(paragraphs)
        else:
            file_obj.status = "failed"
            file_obj.save()
            ActivityLog.objects.create(
                user=file_obj.user,
                action="file_processing_failed",
                metadata={"reason": "unsupported_extension", "file": file_obj.filename}
            )
            return {"status": "failed", "reason": "unsupported_extension"}

        words = [w for w in text.split() if w.strip()]
        count = len(words)

        file_obj.word_count = count
        file_obj.status = "completed"
        file_obj.save()

        ActivityLog.objects.create(
            user=file_obj.user,
            action="file_processed",
            metadata={"file": file_obj.filename, "word_count": count}
        )

        return {"status": "completed", "word_count": count}
    except FileUpload.DoesNotExist:
        return {"status": "failed", "reason": "not_found"}
    except Exception as exc:
        try:
            file_obj.status = "failed"
            file_obj.save()
            ActivityLog.objects.create(
                user=file_obj.user,
                action="file_processing_failed",
                metadata={"error": str(exc)}
            )
        except:
            pass
        raise self.retry(exc=exc, countdown=10, max_retries=3)
