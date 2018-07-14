import React from 'react';
import Select from 'react-select';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import '../../css/react-select.css';
import DrugSelectBoxActions from '../../Redux/Actions/HomeActions/DrugSelectBoxActions';
import { drawTimeSeriesGraph, callOrNotDrugAndEffectData } from '../../Helpers/graphTools/graphing';
// console.log(rxnormDrugs[0])

class DrugSelectBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // options: rxnormDrugs,
      // value: '', //[],
      // request: null
    };
    // this.handleSelectChange = this.handleSelectChange.bind(this);
    // this.handleDrugChange = this.handleDrugChange.bind(this);
    this.formSelectedDrugString = this.formSelectedDrugString.bind(this);
    this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
  }

  apiTopOutcomes(value) {
    let { handleDrugChange, formSelectedDrugString, props } = this;
    let { numOutcomeResults: numResults, drugSelectBoxSetDrug, effectValue, drugSelectBoxDrugChange } = props;
    let selectedDrug = formSelectedDrugString(value);
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

  formSelectedDrugString (value) {
    let selectedDrug;
    try {
      // react-select doesn't sort values. Here, we sort them numerically.
      var selectedDrugArray = value.split(',').map(function(item) {
        return parseInt(item, 10);
      });
      let sortNumber = (a, b) => {
        return a - b;
      };
      selectedDrugArray.sort(sortNumber);
      selectedDrug = selectedDrugArray.join(',');
      if (selectedDrug === 'NaN') {
        selectedDrug = '';
      }
    } catch (err) {
      // console.log("Error! ", err);
      selectedDrug = '';
    }
    return selectedDrug;
  }


  render() {
    const { props, apiTopOutcomes } = this;
    const { value, options } = props;
    return (
      <div className="section select_container">
        <div className="drug_title">Drug</div>
        <Select name="selected-drugs" 
          joinValues multi simpleValue
          value={value}
          placeholder="Select drug(s)..."
          noResultsText="Drug not found"
          options={options}
          onChange={apiTopOutcomes}/>
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  let { HomeReducer } = state;
  let { numOutcomeResults, drugSelectBox, effectSelectBox, drugs } = HomeReducer;
  let { value, options } = drugSelectBox;
  let { value: effectValue } = effectSelectBox;
  // console.log('value',value, options, effectValue)
  return {
    numOutcomeResults,
    value,
    options,
    drugs,
    effectValue
  };
};
  
const mapDispatchToProps = (dispatch) => {
  const { drugSelectBoxDrugChange, drugSelectBoxSetDrug } = DrugSelectBoxActions;
  return {
    drugSelectBoxDrugChange: (newDrug, topOutcomes, drugHasNoModel) => {
      dispatch(drugSelectBoxDrugChange(newDrug, topOutcomes, drugHasNoModel));
    },
    drugSelectBoxSetDrug: (value) => {
      dispatch(drugSelectBoxSetDrug(value));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(DrugSelectBox));