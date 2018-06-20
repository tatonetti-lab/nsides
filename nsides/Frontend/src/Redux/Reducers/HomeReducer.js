import { rxnormDrugs } from '../../Helpers/drugs-top-200';

let start = {
  drugEffectModels: [],
  selectedModel: null,
  drugs: '',
  numOutcomeResults: 'all',
  submitNewModelOption: '',
  drugSelectBox: {
    value: null, //id
    options: rxnormDrugs 
  },
  effectSelectBox: {
    suggestions: [],
    text: '', //text in input field
    value: null, // object containing value and label of selected effect
    outcome: '', //name
    outcomeOptions: [] 
  }
};

const HomeReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  let { effectSelectBox, drugSelectBox } = newState;
  let data = action.payload;
  // console.log('home state', newState, 'data', data);
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
      if (data.value === '') {
        effectSelectBox.value = null;
      }
      effectSelectBox.outcomeOptions = [{
        label: `Loading...`,
        value: `N/A`
      }];
      return newState;
    }
    case `HOMEACTION DRUGSELECTBOX DRUG CHANGE`: {
      newState.drugs = data.newDrugs;
      newState.submitNewModelOption = data.drugHasNoModel;
      effectSelectBox.outcome = '';
      effectSelectBox.outcomeOptions = data.topOutcomes;
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX EFFECT CHANGE`: {
      effectSelectBox.value = data.value;
      // newState.drugs = data.drugs;
      // console.log('effect select box', data);
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX SET TEXT`: {
      effectSelectBox.text = data;
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX SET SUGGESTIONS`: {
      effectSelectBox.suggestions = data;
      return newState
    }
    default: {
      return state;
    }
  }
}

export default HomeReducer;