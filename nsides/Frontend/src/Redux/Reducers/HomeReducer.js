import { rxnormIngredients } from '../../Helpers/drugs-top-200';
import effects from '../../Helpers/effects-7084';

const start = {
  drugEffectModels: [],
  selectedModel: null,
  drugs: '',
  numOutcomeResults: 'all',
  drugHasNoModel: '',
  drugSelectBox: {
    value: null, //id
    options: rxnormIngredients
  },
  effectSelectBox: {
    suggestions: [],
    text: '', //text in input field
    value: null, // object containing value and label of selected effect
    outcome: '', //name
    outcomeOptions: effects
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
    case `HOMEACTION DRUGSELECTBOX SET DRUG`: {  //initial selection of drug, trigger loading for effect box
      drugSelectBox.value = data.value;
      // if (data.value === '') {
      //   effectSelectBox.value = null;
      // }
      effectSelectBox.outcomeOptions = [{
        label: `Loading...`,
        value: `N/A`
      }];
      return newState;
    }
    case `HOMEACTION DRUGSELECTBOX DRUG CHANGE`: {  //after initial selection update with retrieved data
      newState.drugs = data.newDrugs;
      newState.drugHasNoModel = data.drugHasNoModel;
      // effectSelectBox.outcome = '';
      if (data.topOutcomes.length) {
        effectSelectBox.outcomeOptions = data.topOutcomes;
      } else {
        effectSelectBox.outcomeOptions = effects;
      }
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX EFFECT CHANGE`: {
      let { effect, drugOptions } = data;
      effectSelectBox.value = effect;
      effectSelectBox.outcome = effect.label;
      if (drugOptions) {
        drugSelectBox.options = drugOptions;
      }
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX SET TEXT`: {
      effectSelectBox.text = data;
      if (data.length === 0) {
        console.log('cleared')
        drugSelectBox.options = rxnormIngredients;
        newState.effectSelectBox = {
          suggestions: [],
          text: '', //text in input field
          value: null, // object containing value and label of selected effect
          outcome: '', //name
          outcomeOptions: effects
        }
      }
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX SET SUGGESTIONS`: {
      effectSelectBox.suggestions = data;
      return newState
    }
    default: {
      return newState;
    }
  }
}

export default HomeReducer;