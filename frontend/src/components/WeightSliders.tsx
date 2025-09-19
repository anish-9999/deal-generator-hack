import type { WeightConfig } from '../types'

interface WeightSlidersProps {
  weights: WeightConfig
  onWeightChange: (weights: WeightConfig) => void
}

const presets = {
  balanced: { team: 20, market: 20, product: 20, traction: 20, moat: 20 },
  teamFocused: { team: 40, market: 15, product: 15, traction: 15, moat: 15 },
  marketFocused: { team: 15, market: 40, product: 15, traction: 15, moat: 15 },
  tractionFocused: { team: 15, market: 15, product: 15, traction: 40, moat: 15 },
  defensibilityFocused: { team: 15, market: 15, product: 15, traction: 15, moat: 40 }
}

const WeightSliders: React.FC<WeightSlidersProps> = ({ weights, onWeightChange }) => {
  const handleSliderChange = (category: keyof WeightConfig, value: number) => {
    const newWeights = { ...weights, [category]: value }

    // Normalize to ensure total equals 100
    const total = Object.values(newWeights).reduce((sum, val) => sum + val, 0)
    if (total !== 100) {
      const factor = 100 / total
      Object.keys(newWeights).forEach(key => {
        newWeights[key as keyof WeightConfig] = Math.round(newWeights[key as keyof WeightConfig] * factor)
      })
    }

    onWeightChange(newWeights)
  }

  const applyPreset = (preset: WeightConfig) => {
    onWeightChange(preset)
  }

  const total = Object.values(weights).reduce((sum, val) => sum + val, 0)

  return (
    <div className="weight-sliders">
      <div className="presets">
        <h3>Quick Presets</h3>
        <div className="preset-buttons">
          <button onClick={() => applyPreset(presets.balanced)}>
            Balanced
          </button>
          <button onClick={() => applyPreset(presets.teamFocused)}>
            Team Focused
          </button>
          <button onClick={() => applyPreset(presets.marketFocused)}>
            Market Focused
          </button>
          <button onClick={() => applyPreset(presets.tractionFocused)}>
            Traction Focused
          </button>
          <button onClick={() => applyPreset(presets.defensibilityFocused)}>
            Defensibility Focused
          </button>
        </div>
      </div>

      <div className="sliders">
        <div className="slider-group">
          <label htmlFor="team-slider">
            Team ({weights.team}%)
          </label>
          <input
            id="team-slider"
            type="range"
            min="0"
            max="100"
            value={weights.team}
            onChange={(e) => handleSliderChange('team', parseInt(e.target.value))}
            className="slider"
          />
        </div>

        <div className="slider-group">
          <label htmlFor="market-slider">
            Market ({weights.market}%)
          </label>
          <input
            id="market-slider"
            type="range"
            min="0"
            max="100"
            value={weights.market}
            onChange={(e) => handleSliderChange('market', parseInt(e.target.value))}
            className="slider"
          />
        </div>

        <div className="slider-group">
          <label htmlFor="product-slider">
            Product ({weights.product}%)
          </label>
          <input
            id="product-slider"
            type="range"
            min="0"
            max="100"
            value={weights.product}
            onChange={(e) => handleSliderChange('product', parseInt(e.target.value))}
            className="slider"
          />
        </div>

        <div className="slider-group">
          <label htmlFor="traction-slider">
            Traction ({weights.traction}%)
          </label>
          <input
            id="traction-slider"
            type="range"
            min="0"
            max="100"
            value={weights.traction}
            onChange={(e) => handleSliderChange('traction', parseInt(e.target.value))}
            className="slider"
          />
        </div>

        <div className="slider-group">
          <label htmlFor="moat-slider">
            Moat ({weights.moat}%)
          </label>
          <input
            id="moat-slider"
            type="range"
            min="0"
            max="100"
            value={weights.moat}
            onChange={(e) => handleSliderChange('moat', parseInt(e.target.value))}
            className="slider"
          />
        </div>
      </div>

      <div className={`total ${total !== 100 ? 'warning' : ''}`}>
        Total: {total}%
        {total !== 100 && <span> (Auto-normalized to 100%)</span>}
      </div>
    </div>
  )
}

export default WeightSliders