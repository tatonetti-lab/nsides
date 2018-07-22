// nSides EffectSelectBox, Updated July 2017

// Copyright (C) 2017, Tatonetti Lab
// Tal Lorberbaum <tal.lorberbaum@columbia.edu>
// Victor Nwankwo <vtn2106@cumc.columbia.edu>
// Joe Romano <dr2160@cumc.columbia.edu>
// Ram Vanguri <rami.vanguri@columbia.edu>
// Nicholas P. Tatonetti <nick.tatonetti@columbia.edu>
// All rights reserved.

// This site is released under a CC BY-NC-SA 4.0 license.
// For full license details see LICENSE.txt at 
// https://github.com/tatonetti-lab/nsides or go to:
// http://creativecommons.org/licenses/by-nc-sa/4.0/
import React from 'react';
import Select from 'react-select';
import '../../css/react-select.css';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import EffectSelectBoxActions from '../../Redux/Actions/HomeActions/EffectSelectBoxActions';
import { callOrNotDrugAndEffectData } from '../../Helpers/graphTools/graphing';

class EffectSelectBox extends React.Component {
	// displayName: 'EffectSelectBox';
	constructor (props) {
    super(props);
    this.state = {      
    };
    this.filterOptions = this.filterOptions.bind(this);
    this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
  }

  filterOptions(options, typedString) {
    let label;
    typedString = typedString.toLowerCase();

    let filtered = options.filter(option => {
      label = option.label.toLowerCase();
      return label.includes(typedString);
    });

    // console.log(options.length, filtered.length, typedString);

    if (filtered.length > 1000) {
      return [];
    } else {
      return filtered;
    }
  }

  apiTopOutcomes(value) {
    let { numOutcomeResults: numResults, drugSelectBoxSetDrug, effectValue, drugSelectBoxDrugChange } = this.props;
    drugSelectBoxSetDrug(value);
    
    // var numResults = this.props.numOutcomeResults;
    var outcomeOptions;
    console.log("selectedDrug", selectedDrug, "numResults", numResults, 'value', value);

    callOrNotDrugAndEffectData(selectedDrug, effectValue);
    if (value.length > 0) {
      var api_call = '/api/effectsFromDrugs/query?drugs=' + selectedDrug;
      // console.log('apicall', api_call);
      axios(api_call)
        .then((j) => {
          j = j.data;
          if (j.topOutcomes.length > 0) {
            outcomeOptions = j.topOutcomes;
            // console.log("outcomeOptions", outcomeOptions.map(item => JSON.stringify(item)).join(', \n'));
            drugSelectBoxDrugChange(selectedDrug, outcomeOptions, '');
          } else {
            drugSelectBoxDrugChange('', [], 'no data for this combination');
          }
        })
    } else {
      drugSelectBoxDrugChange('', [], '')
    }
  }
    
	render () {        
    // console.log(this.props);
    const { props, apiTopOutcomes } = this;
    const { value, options, suggestions } = props;
    // console.log('input', inputProps, suggestions);

    return (
      <div className="section select_container_effect">
        <div className="effect_title">Effect</div>
        <Select name="selected-effects" 
          value={value}
          placeholder="Type an effect..."
          noResultsText="Effect not found"
          options={suggestions}
          onChange={apiTopOutcomes}/>
      </div>
    );
	}
}

const mapStateToProps = (state) => {
  const HomeReducer = state.HomeReducer;
  const { submitNewModelOption, drugs, effectSelectBox, drugSelectBox } = HomeReducer;
  const { value, outcome, outcomeOptions, text, suggestions } = effectSelectBox;
  // console.log(state);
  return {
    suggestions,
    text,
    outcome,
    outcomeOptions,
    drugs,
    submitNewModelOption,
    value
  };
};
  
const mapDispatchToProps = (dispatch) => {
  const { effectSelectBoxEffectChange, setSelectionSuggestions, setEffectBoxText } = EffectSelectBoxActions;
  return {
    setEffectBoxText: (value) => {
      dispatch(setEffectBoxText(value));
    },
    setSelectionSuggestions: (suggestions) => {
      dispatch(setSelectionSuggestions(suggestions));
    },
    effectSelectBoxEffectChange: (effect, drugOptions) => {
      dispatch(effectSelectBoxEffectChange(effect, drugOptions));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(EffectSelectBox));
