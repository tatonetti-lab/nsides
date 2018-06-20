import React from 'react';
import Select from 'react-select';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import '../../css/react-select.css';
import DrugSelectBoxActions from '../../Redux/Actions/HomeActions/DrugSelectBoxActions';
import { drawTimeSeriesGraph, callOrNotDrugAndEffectData } from '../../Helpers/graphTools/graphing';
// console.log(rxnormDrugs[0])
var request = null;
class DrugSelectBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // options: rxnormDrugs,
      // value: '', //[],
      // request: null
    };
    // this.handleSelectChange = this.handleSelectChange.bind(this);
    this.handleDrugChange = this.handleDrugChange.bind(this);
    this.formSelectedDrugString = this.formSelectedDrugString.bind(this);
    this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
  }

  // componentDidMount () {

  // }

  apiTopOutcomes(value) {
    let { handleDrugChange, formSelectedDrugString } = this;
    let { numOutcomeResults: numResults, boundDrugSelectBoxSetDrug } = this.props;
    let selectedDrug = formSelectedDrugString(value);
    boundDrugSelectBoxSetDrug(value);
    
    // var numResults = this.props.numOutcomeResults;
    var outcomeOptions;

    console.log("selectedDrug", selectedDrug, "numResults", numResults, 'value', value);

    if (selectedDrug === '') {
      // console.log('No selectedDrug; no API call necessary');
      handleDrugChange('', [], '');
    } else {
      var api_call = '/api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=' + numResults + '&drugs=' + selectedDrug;
      // console.log('apicall', api_call);
      axios({
        method: 'GET',
        url: api_call
      })
        .then((j) => {
          j = j.data;
          outcomeOptions = j["results"][0]["topOutcomes"];
          // console.log("outcomeOptions", outcomeOptions.map(item => JSON.stringify(item)).join(', \n'));
          handleDrugChange(selectedDrug, outcomeOptions, '')
        })
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
  
  handleDrugChange(drugs, topOutcomes, drugHasNoModel) {
    let { drugChange, dateformat, effectValue } = this.props;
    drugChange(drugs, topOutcomes, drugHasNoModel)
    let title1, title2;
    if (drugHasNoModel !== '') {
      title1 = '';
    } else {
      title1 = "Select a drug and effect";
    }
    callOrNotDrugAndEffectData(drugs, effectValue, title1)
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
    drugChange: (newDrug, topOutcomes, drugHasNoModel) => {
      dispatch(drugSelectBoxDrugChange(newDrug, topOutcomes, drugHasNoModel));
    },
    boundDrugSelectBoxSetDrug: (value) => {
      dispatch(drugSelectBoxSetDrug(value));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(DrugSelectBox));