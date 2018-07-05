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
// import Select from 'react-select';
import Autosuggest from 'react-autosuggest';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import EffectSelectBoxActions from '../../Redux/Actions/HomeActions/EffectSelectBoxActions';
import { drawTimeSeriesGraph, showLoading, callOrNotDrugAndEffectData } from '../../Helpers/graphTools/graphing';
import { escapeRegexCharacters } from '../../Helpers/utility';
import '../../css/react-Autosuggest.css';

class EffectSelectBox extends React.Component {
	// displayName: 'EffectSelectBox';
	constructor (props) {
    super(props);
    this.state = {      
    };
    this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this);
    this.onSuggestionsClearRequested = this.onSuggestionsClearRequested.bind(this);
    this.getSuggestionValue = this.getSuggestionValue.bind(this);
    this.getSuggestions = this.getSuggestions.bind(this);
    this.renderSuggestion = this.renderSuggestion.bind(this);
    this.onChange = this.onChange.bind(this);    
	}
  
  getSuggestions(value) {
    const escapedValue = escapeRegexCharacters(value.trim());
    let { suggestions, outcomeOptions } = this.props;
    let options = suggestions.length > 0 ? suggestions : outcomeOptions;
    // console.log('options', options, suggestions, outcomeOptions);
    if (escapedValue === '') {
      return [];
    }
  
    const regex = new RegExp(escapedValue, 'i');
    return options.filter((option) => {
      // console.log(option);
      return regex.test(option.label);
    });
  }

  onSuggestionsFetchRequested({ value }) {
    let { setSelectionSuggestions } = this.props;
    let filteredSuggestions = this.getSuggestions(value);
    // console.log('length of suggestions is ', suggestions.length);
    if (filteredSuggestions.length < 1001) {
      setSelectionSuggestions(filteredSuggestions);
    } else {
      setSelectionSuggestions([]);
    }
  };

  onSuggestionsClearRequested() {
    this.props.setSelectionSuggestions([]);
  };

  getSuggestionValue(suggestion) {
    console.log('selected',suggestion);
    let { effectSelectBoxEffectChange, drugs } = this.props;
    if (drugs.length) {
      effectSelectBoxEffectChange(suggestion);
    } else {
      let url = '/api/drugsFromEffect/query?effect=' + suggestion.value;
      axios(url)
        .then(result => {
          let drugOptions = result.data.topOutcomes;
          effectSelectBoxEffectChange(suggestion, drugOptions);
        })
    }
    callOrNotDrugAndEffectData(drugs, suggestion);
    return suggestion.label;
  }

  renderSuggestion(suggestion) {
    // console.log(suggestion, 'k');
    return (
      <div>{suggestion.label}</div>
    );
  }

  onChange(event, { newValue, method }) {
    // console.log('new', newValue);
    this.props.setEffectBoxText(newValue);
  };
    
	render () {        
    // console.log(this.props);
    const { props, handleSelectChange } = this;
    const { text, options, suggestions } = props;
    const inputProps = {
      placeholder: 'Type an effect',
      value: text,
      onChange: this.onChange
    };
    // console.log('input', inputProps, suggestions);

    return (
      <div className="section select_container_effect">
        <div className="effect_title">Effect</div>
        <Autosuggest
          suggestions={suggestions} //
          onSuggestionsFetchRequested={this.onSuggestionsFetchRequested} //
          onSuggestionsClearRequested={this.onSuggestionsClearRequested} // 
          getSuggestionValue={this.getSuggestionValue} //get the name of the suggestion
          renderSuggestion={this.renderSuggestion} //
          inputProps={inputProps}/>
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
