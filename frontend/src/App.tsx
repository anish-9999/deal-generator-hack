import { useState } from 'react'
import FileUpload from './components/FileUpload'
import WeightSliders from './components/WeightSliders'
import GenerateButton from './components/GenerateButton'
import DealNoteDisplay from './components/DealNoteDisplay'
import type { WeightConfig } from './types'
import './App.css'

function App() {
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([])
  const [weights, setWeights] = useState<WeightConfig>({
    team: 20,
    market: 20,
    product: 20,
    traction: 20,
    moat: 20
  })
  const [dealNote, setDealNote] = useState<string>('')
  const [isGenerating, setIsGenerating] = useState(false)

  const handleFileUpload = (fileId: string) => {
    setUploadedFiles(prev => [...prev, fileId])
  }

  const handleWeightChange = (newWeights: WeightConfig) => {
    setWeights(newWeights)
  }

  const handleGenerate = async () => {
    if (uploadedFiles.length === 0) {
      alert('Please upload at least one file')
      return
    }

    setIsGenerating(true)
    try {
      const response = await fetch('http://localhost:8080/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fileIds: uploadedFiles,
          weights: weights
        })
      })

      const data = await response.json()
      if (data.success) {
        setDealNote(data.dealNote)
      } else {
        alert('Error generating deal note: ' + data.message)
      }
    } catch (error) {
      alert('Error connecting to server')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="app">
      <div className="app-container">
        <header className="app-header">
          <h1>Deal Note Generator</h1>
          <p>Turn messy founder materials into an investor‑ready Deal Note</p>
        </header>

        <main className="app-main">
          <div className="app-grid">
          <div className="upload-section">
            <h2>Upload Documents</h2>
            <FileUpload onFileUpload={handleFileUpload} />
            {uploadedFiles.length > 0 && (
              <div className="uploaded-files">
                <h3>Uploaded Files ({uploadedFiles.length})</h3>
                <ul>
                  {uploadedFiles.map((fileId, index) => (
                    <li key={index}>{fileId}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="weights-section">
            <h2>Investment Criteria Weights</h2>
            <WeightSliders weights={weights} onWeightChange={handleWeightChange} />
          </div>

          <div className="generate-section">
            <GenerateButton
              onGenerate={handleGenerate}
              isGenerating={isGenerating}
              disabled={uploadedFiles.length === 0}
            />
          </div>

          {dealNote && (
            <div className="result-section">
              <h2>Generated Deal Note</h2>
              <DealNoteDisplay dealNote={dealNote} />
            </div>
          )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
