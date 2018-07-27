const effectSelectBoxEffectChange = (topOutcomes) => {
  return {
    type: `HOMEACTION EFFECTSELECTBOX EFFECT CHANGE`,
    payload: {
      topOutcomes
    }
  }
};

const effectSelectBoxSetEffect = (value) => {
  return {
    type: `HOMEACTION EFFECTSELECTBOX SET EFFECT`,
    payload: {
      value
    }
  }
};

const setEffectBoxText = (text) => {
  return {
    type: `HOMEACTION EFFECTSELECTBOX SET TEXT`,
    payload: text
  }
};

const setSelectionSuggestions = (suggestions) => {
  return {
    type: `HOMEACTION EFFECTSELECTBOX SET SUGGESTIONS`,
    payload: suggestions
  }
};


let all = {
  effectSelectBoxEffectChange,
  effectSelectBoxSetEffect,
  setEffectBoxText,
  setSelectionSuggestions
};

export default all;
export {
  effectSelectBoxEffectChange,
  effectSelectBoxSetEffect,
  setEffectBoxText,
  setSelectionSuggestions
}