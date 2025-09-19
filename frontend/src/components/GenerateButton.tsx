interface GenerateButtonProps {
  onGenerate: () => void
  isGenerating: boolean
  disabled: boolean
}

const GenerateButton: React.FC<GenerateButtonProps> = ({ onGenerate, isGenerating, disabled }) => {
  return (
    <div className="generate-button-container">
      <button
        className={`generate-button ${isGenerating ? 'generating' : ''}`}
        onClick={onGenerate}
        disabled={disabled || isGenerating}
      >
        {isGenerating ? (
          <>
            <div className="spinner"></div>
            Generating Deal Note...
          </>
        ) : (
          'Generate Deal Note'
        )}
      </button>

      {disabled && !isGenerating && (
        <p className="button-help">Upload at least one document to generate a deal note</p>
      )}
    </div>
  )
}

export default GenerateButton