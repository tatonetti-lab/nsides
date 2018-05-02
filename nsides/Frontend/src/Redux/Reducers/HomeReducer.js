import { rxnormDrugs } from '../../Helpers/drugs-top-200';

let start = {
  drugEffectModels: [],
  selectedModel: null,
  dateformat: '%Y',
  request: null,
  drugs: '',
  numOutcomeResults: 'all',
  submitNewModelOption: '',
  drugSelectBox: {
    value: '',
    options: rxnormDrugs
  },
  effectSelectBox: {
    value: '',
    outcome: '',
    outcomeOptions: []
  }
};

const HomeReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  let { effectSelectBox, drugSelectBox } = newState;
  let data = action.payload;
  // console.log('home state', newState);
  switch (action.type) {
    case `HOMEACTION SET DRUG EFFECT MODELS`: {
      newState.drugEffectModels = data;
      // console.log('new drug models are', data);
      return newState;
    }
    case `HOMEACTION SET SELECTED MODEL`: {
      newState.selectedModel = data;
      return newState;
    }
    case `HOMEACTION DRUGSELECTBOX SET DRUG`: {
       drugSelectBox.value = data.value;
      return newState;
    }
    case `HOMEACTION DRUGSELECTBOX DRUG CHANGE`: {
      newState.drugs = data.newDrug;
      newState.submitNewModelOption = data.drugHasNoModel;
      effectSelectBox.outcome = '';
      effectSelectBox.outcomeOptions = data.topOutcomes;
      return newState;
    }
    case `HOME ACTION EFFECTSELECTBOX EFFECT CHANGE`: {
      effectSelectBox.value = data.value;
      newState.outcome = data.outcome;
      newState.drugs = data.drugs;
      console.log('effect select box', data);
      return newState
    }
    default: {
      return newState;
    }
  }
}

export default HomeReducer;