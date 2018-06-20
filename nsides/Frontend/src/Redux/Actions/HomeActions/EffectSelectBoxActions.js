const effectSelectBoxEffectChange = (value) => {
  console.log(value);
  return {
    type: `HOMEACTION EFFECTSELECTBOX EFFECT CHANGE`,
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
  setEffectBoxText,
  setSelectionSuggestions
};

export default all;
export {
  effectSelectBoxEffectChange,
  setEffectBoxText,
  setSelectionSuggestions
}