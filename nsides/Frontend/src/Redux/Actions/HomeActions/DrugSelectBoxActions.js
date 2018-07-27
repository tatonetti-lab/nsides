const setDrugEffectModels = (data) => {
  let action = {
    type: `HOMEACTION SET DRUG EFFECT MODELS`,
    payload: data
  }
  return action;
};

const setSelectedModel = (modelType) => {
  return {
    type: `HOMEACTION SET SELECTED MODEL`,
    payload: modelType
  }
};

const drugSelectBoxDrugChange = (topOutcomes, drugHasNoModel) => {
  return {
    type: `HOMEACTION DRUGSELECTBOX DRUG CHANGE`,
    payload: {
      topOutcomes,
      drugHasNoModel
    }
  }
};

const drugSelectBoxSetDrug = (value) => {
  return {
    type: `HOMEACTION DRUGSELECTBOX SET DRUG`,
    payload: {
      value
    }
  }
};

let all = {
  setDrugEffectModels,
  setSelectedModel,
  drugSelectBoxDrugChange,
  drugSelectBoxSetDrug
};

export default all;
export {
  setDrugEffectModels,
  setSelectedModel,
  drugSelectBoxDrugChange,
  drugSelectBoxSetDrug
}