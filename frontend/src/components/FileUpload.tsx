import { useState, useRef } from 'react'

interface FileUploadProps {
  onFileUpload: (fileId: string) => void
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const files = Array.from(e.dataTransfer.files)
    uploadFiles(files)
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    uploadFiles(files)
  }

  const uploadFiles = async (files: File[]) => {
    for (const file of files) {
      setIsUploading(true)
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch('http://localhost:8080/api/upload', {
          method: 'POST',
          body: formData
        })

        const data = await response.json()
        if (data.success) {
          onFileUpload(data.fileId)
        } else {
          alert(`Error uploading ${file.name}: ${data.message}`)
        }
      } catch (error) {
        alert(`Error uploading ${file.name}: Network error`)
      }
    }
    setIsUploading(false)
  }

  const handleClick = () => {
    fileInputRef.current?.click()
  }

  return (
    <div className="file-upload">
      <div
        className={`upload-area ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          multiple
          accept=".pdf,.doc,.docx,.ppt,.pptx,.txt"
          style={{ display: 'none' }}
        />

        {isUploading ? (
          <div className="upload-status">
            <div className="spinner"></div>
            <p>Uploading files...</p>
          </div>
        ) : (
          <div className="upload-prompt">
            <div className="upload-icon">📁</div>
            <p>Drag and drop files here or click to browse</p>
            <p className="file-types">Supports: PDF, DOC, DOCX, PPT, PPTX, TXT</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default FileUpload