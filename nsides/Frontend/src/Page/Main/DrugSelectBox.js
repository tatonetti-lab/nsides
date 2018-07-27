import React from 'react';
import Select from 'react-select';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import '../../css/react-select.css';
import DrugSelectBoxActions from '../../Redux/Actions/HomeActions/DrugSelectBoxActions';
import { callOrNotDrugAndEffectData } from '../../Helpers/graphTools/graphing';
// console.log(rxnormDrugs[0])

class DrugSelectBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
    };
    this.formSelectedDrugString = this.formSelectedDrugString.bind(this);
    this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
  }

  apiTopOutcomes(value) {
    let { formSelectedDrugString, props } = this;
    let { drugSelectBoxSetDrug, effectValue, drugSelectBoxDrugChange } = props;
    let selectedDrug = formSelectedDrugString(value);
    drugSelectBoxSetDrug(value);
    
    var outcomeOptions;
    console.log("selectedDrug", selectedDrug, 'value', value);
    if (effectValue != null) {
      callOrNotDrugAndEffectData(selectedDrug, effectValue);
    }
    if (value.length > 0) {
      var api_call = '/api/effectsFromDrugs/query?drugs=' + selectedDrug;
      // console.log('apicall', api_call);
      axios(api_call)
        .then((j) => {
          j = j.data;
          if (j.topOutcomes.length > 0) {
            outcomeOptions = j.topOutcomes;
            // console.log("outcomeOptions", outcomeOptions.map(item => JSON.stringify(item)).join(', \n'));
            drugSelectBoxDrugChange(outcomeOptions, '');
          } else {
            drugSelectBoxDrugChange([], 'no data for this combination');
          }
        })
    } else {
      drugSelectBoxDrugChange([], '')
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
    // console.log(options);
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
  let { drugSelectBox, effectSelectBox } = HomeReducer;
  let { value, options } = drugSelectBox;
  let { value: effectValue } = effectSelectBox;
  // console.log('value',value, options, effectValue)
  return {
    value,
    options,
    effectValue
  };
};
  
const mapDispatchToProps = (dispatch) => {
  const { drugSelectBoxDrugChange, drugSelectBoxSetDrug } = DrugSelectBoxActions;
  return {
    drugSelectBoxDrugChange: (topOutcomes, drugHasNoModel) => {
      console.log('drug change');
      dispatch(drugSelectBoxDrugChange(topOutcomes, drugHasNoModel));
    },
    drugSelectBoxSetDrug: (value) => {
      dispatch(drugSelectBoxSetDrug(value));
    }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(DrugSelectBox));