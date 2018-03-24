const setDrugEffectData = (data) => {
  let action = {
    type: `HOMEACTION SET DRUG EFFECT DATA`,
    payload: data
  }
  return action;
};

const setSelectedModel = (modelType) => {
  return {
    type: `HOMEACTION SET SELECTED MODEL`,
    payload: modelType
  }
}
let all = {
  setDrugEffectData
};

export default all;
export {
  setDrugEffectData,
  setSelectedModel
};