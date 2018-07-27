import { rxnormIngredients } from '../../Helpers/drugs-reference';
import effects from '../../Helpers/effects-7084';

const start = {
  drugEffectModels: [],
  selectedModel: null,
  numOutcomeResults: 'all',
  drugHasNoModel: '',
  drugSelectBox: {
    value: null, //id
    options: rxnormIngredients
  },
  effectSelectBox: {
    value: null, // id
    suggestions: effects
  }
};

const HomeReducer = (state = start, action) => {
  let newState = Object.assign({}, state);
  let { effectSelectBox, drugSelectBox } = newState;
  let data = action.payload;
  // console.log('home state', newState, 'data', data, action.type);
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
      const { value } = data;
      drugSelectBox.value = value;
      // if (effectSelectBox.value === null) {
      //   effectSelectBox.suggestions = [{
      //     label: `Loading...`,
      //     value: `N/A`
      //   }];
      // }
      return newState;
    }
    case `HOMEACTION DRUGSELECTBOX DRUG CHANGE`: {  //after initial selection update with retrieved data
      const { drugHasNoModel, topOutcomes } = data;
      newState.drugHasNoModel = drugHasNoModel;
      if (topOutcomes.length) { // if drug has outcomes
        // console.log('eff changed', data.topOutcomes[0]);
        effectSelectBox.suggestions = topOutcomes;
      } else {
        effectSelectBox.suggestions = effects;
      }
      return newState;
    }
    case `HOMEACTION EFFECTSELECTBOX SET EFFECT`: {
      let { value } = data;
      effectSelectBox.value = value;
      // if (drugSelectBox.value === null) {
      //   drugSelectBox.options = [{
      //     label: `Loading...`,
      //     value: `N/A`
      //   }];
      // }
      return newState
    }
    case `HOMEACTION EFFECTSELECTBOX EFFECT CHANGE`: {  //after initial selection update with retrieved data
      let { topOutcomes } = data;
      if (topOutcomes.length) {
        // console.log('eff changed', data.topOutcomes[0]);
        drugSelectBox.options = topOutcomes;
      } else {
        drugSelectBox.options = rxnormIngredients;
      }
      return newState;
    }
    // case `HOMEACTION EFFECTSELECTBOX SET TEXT`: {
    //   effectSelectBox.text = data;
    //   var originalOptions = effectSelectBox.outcomeOptions;
    //   if (data.length === 0) {
    //     console.log('cleared')
    //     drugSelectBox.options = rxnormIngredients;
    //     newState.effectSelectBox = {
    //       suggestions: [],
    //       text: '', //text in input field
    //       value: null, // object containing value and label of selected effect
    //       outcome: '', //name
    //     };

    //     if (drugSelectBox.value === null) {
    //       newState.effectSelectBox.outcomeOptions = effects;
    //     } else {
    //       newState.effectSelectBox.outcomeOptions = originalOptions;
    //     }
    //   }
    //   return newState;
    // }
    default: {
      return newState;
    }
  }
}

export default HomeReducer;