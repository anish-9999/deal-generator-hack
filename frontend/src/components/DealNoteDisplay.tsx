interface DealNoteDisplayProps {
  dealNote: string
}

const DealNoteDisplay: React.FC<DealNoteDisplayProps> = ({ dealNote }) => {
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(dealNote)
      alert('Deal note copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const downloadAsText = () => {
    const element = document.createElement('a')
    const file = new Blob([dealNote], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = 'deal-note.txt'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div className="deal-note-display">
      <div className="deal-note-actions">
        <button onClick={copyToClipboard} className="action-button">
          📋 Copy to Clipboard
        </button>
        <button onClick={downloadAsText} className="action-button">
          💾 Download as Text
        </button>
      </div>

      <div className="deal-note-content">
        <pre>{dealNote}</pre>
      </div>
    </div>
  )
}

export default DealNoteDisplay