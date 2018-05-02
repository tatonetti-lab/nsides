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

const drugSelectBoxDrugChange = (newDrug, topOutcomes, drugHasNoModel) => {
  return {
    type: `HOMEACTION DRUGSELECTBOX DRUG CHANGE`,
    payload: {
      newDrug,
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
}

const effectSelectBoxEffectChange = (drugs, outcome, value) => {
  console.log(drugs, outcome, value);
  return {
    type: `HOME ACTION EFFECTSELECTBOX EFFECT CHANGE`,
    payload: {
      drugs,
      outcome,
      value
    }
  }
};

let all = {
  setDrugEffectModels,
  setSelectedModel,
  drugSelectBoxDrugChange,
  drugSelectBoxSetDrug,
  effectSelectBoxEffectChange
};

export default all;
export {
  setDrugEffectModels,
  setSelectedModel,
  drugSelectBoxDrugChange,
  drugSelectBoxSetDrug,
  effectSelectBoxEffectChange
};