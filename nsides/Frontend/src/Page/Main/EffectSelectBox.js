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
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import HomeAction from '../../Redux/Actions/HomeActions';
import '../../css/react-select.css';
import { drawTimeSeriesGraph, showLoading } from '../../Helpers/graphing';

class EffectSelectBox extends React.Component {
	// displayName: 'EffectSelectBox';
	constructor (props) {
    super(props);
    this.state = {
			// options: this.props.outcomeOptions,
			// value: this.props.outcome //'', //[],
      // numOutcomeResults: this.props.numOutcomeResults
      // loadingIconStyle: {float:"right", display:"none"},
    };
    this.handleSelectChange = this.handleSelectChange.bind(this);
    this.handleDrugOutcomeChange = this.handleDrugOutcomeChange.bind(this);
	}

	handleSelectChange (value) {
    const { handleDrugOutcomeChange } = this;
    const { drugs } = this.props;
    console.log('effect value', value);
    handleDrugOutcomeChange(drugs, value);
  }
  
  handleDrugOutcomeChange (drugs, value) {
    let { submitNewModelOption, boundSetDrugEffectModels, boundEffectSelectBoxEffectChange, request, dateformat } = this.props;
    const outcome = value === null ? '' : value.value;
    let title1, title2;
    boundEffectSelectBoxEffectChange(drugs, outcome, value);
    showLoading();
    // console.log("newDrug", drugs, "newOutcome", outcome, this);
    
    if ((drugs === "") || (outcome === "")) {
      if (submitNewModelOption !== '') {
        title1 = "";
        title2 = '';
      } else {
        title1 = "Select a drug and effect";
        title2 = '';
      }
      drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
    } else {
      var api_call = "/api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs=" + drugs + "&outcome=" + outcome;
      axios({
        method: 'GET',
        url: api_call
      })
        .then((j) => {
          // console.log("data:");
          j = j.data;
          // console.log('received', j, '\n');
          var data, data2, modelType;// hasModelType = false, foundIndex;
          modelType = j.results[0].model;
          data = j["results"][0]["estimates"];
          data2 = j["results"][0]["nreports"];

          var data1 = data;
          var title1 = "Proportional Reporting Ratio over time";
          var title2 = "Number of reports by year";

          boundSetDrugEffectModels(j.results);
          drawTimeSeriesGraph(data1, data2, title1, title2, dateformat, false, modelType);
        });
    };
  }

//	toggleDisabled (e) {
//		this.setState({ disabled: e.target.checked });
//	}
    
	render () {        
    // console.log(this.props);
    const { props, handleSelectChange } = this;
    const { value, outcomeOptions } = props;

    return (
      <div className="section select_container_effect">
        <div className="effect_title">Effect</div>
        <Select name="selected-effect"
          value={value} //{this.state.value}
          placeholder="Select effect..."
          noResultsText='No effects found'
          options={outcomeOptions}
          onChange={handleSelectChange} />
      </div>
    );
	}
}

const mapStateToProps = (state) => {
  const HomeReducer = state.HomeReducer;
  const { submitNewModelOption, drugs, request, dateformat } = HomeReducer;
  const { value, outcome, outcomeOptions } = HomeReducer.effectSelectBox;
  return {
    outcome,
    outcomeOptions,
    drugs,
    request,
    dateformat,
    submitNewModelOption,
    value
  };
};
  
const mapDispatchToProps = (dispatch) => {
  const { setDrugEffectModels, effectSelectBoxEffectChange } = HomeAction;
  return {
    boundSetDrugEffectModels: (data) => {
      dispatch(setDrugEffectModels(data));
    },
    boundEffectSelectBoxEffectChange: (drugs, outcome, value) => {
      dispatch(effectSelectBoxEffectChange(drugs, outcome, value));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(EffectSelectBox));

// handleDrugOutcomeChange(newDrug, newOutcome) {
//   this.setState({
//     drugs: newDrug,
//     outcome: newOutcome
//   }, () => {
//     let { request, dateformat } = this.state;
//     let title1, title2;
//     console.log("newDrug", newDrug, "newOutcome", newOutcome, this);
    
//     if ((newDrug === "") || (newOutcome === "")) {
//       if (this.state.submitNewModelOption !== '') {
//         title1 = "";
//         title2 = '';
//       } else {
//         title1 = "Select a drug and effect";
//         title2 = '';
//       }
//       drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
//     } else {
//       var api_call = "/api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs=" + newDrug + "&outcome=" + newOutcome;
//       // console.log(api_call);
//       request = fetch(api_call) // http://stackoverflow.com/a/41059178
//         .then(function (response) {
//           return response.json();
//         })
//         .then(function (j) {
//           let { setdrugEffectModels } = this.props;
//           // console.log("data:");
//           console.log('received', j, '\n');
//           var data, data2, modelType;// hasModelType = false, foundIndex;
//           modelType = j.results[0].model;
//           data = j["results"][0]["estimates"];
//           data2 = j["results"][0]["nreports"];
//           // if (selectedModel !== null) {
//           //   for (var i = 0; i < j.results.length; i++) {
//           //     if (j.results[i].model === selectedModel) {
//           //       hasModelType = true;
//           //       foundIndex = i;
//           //       break;
//           //     }
//           //   }
//           // }
//           // console.log('has modeltype',hasModelType)
//           // if (hasModelType) {
//           //   modelType = selectedModel;
//           //   data = j.results[foundIndex].estimates;
//           //   data2 = j.results[foundIndex].nreports;
//           // } else {
//           //   modelType = j.results[0].model;
//           //   data = j["results"][0]["estimates"];
//           //   data2 = j["results"][0]["nreports"];
//           //   setSelectedModel(modelType);
//           // }
//           // console.log('data', data, 'data2', data2);
//           // console.log("modelType: ", modelType);
//           // console.log("drug-effect data", data);
//           // console.log("number of reports by year", data2);

//           /* Set variables */
//           var data1 = data;
//           var title1 = "Proportional Reporting Ratio over time";
//           var title2 = "Number of reports by year";
//           // console.log('modelType', modelType)
//           // setSelectedModel(modelType);
//           // let select = document.querySelector(`select.model-types`);
//           // if (select !== null) {
//           //   select.value = modelType;
//           // }
//           setdrugEffectModels(j.results);
//           drawTimeSeriesGraph(data1, data2, title1, title2, dateformat, false, modelType);
//         }.bind(this))
//         // .catch(function (ex) {
//         //   // console.log('Parsing failed', ex);
//         //   request = null;
//         //   var title1 = "Select a drug and effect"; //"No results found";
//         //   var title2 = '';
//         //   console.log('hi',ex)
//         //   drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
//         // });
//     }
//   });
// }