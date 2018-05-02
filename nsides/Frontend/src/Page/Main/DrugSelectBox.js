import React from 'react';
import Select from 'react-select';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import axios from 'axios';
import '../../css/react-select.css';
import HomeActions from '../../Redux/Actions/HomeActions';
import { drawTimeSeriesGraph } from '../../Helpers/graphing';
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

  // handleSelectChange(value) {
  //   // this.setState({ value }, () => {
  //   //   this.apiTopOutcomes();
  //   // });
  //   let { apiTopOutcomes } = this;
  //   apiTopOutcomes(value);
  // }

  apiTopOutcomes(value) {
    let { handleDrugChange, formSelectedDrugString } = this;
    let { numOutcomeResults: numResults, boundDrugSelectBoxSetDrug } = this.props;
    let selectedDrug = formSelectedDrugString(value);
    boundDrugSelectBoxSetDrug(value);
    
    // var numResults = this.props.numOutcomeResults;
    var outcomeOptions;

    console.log("selectedDrug", selectedDrug, "numResults", numResults);

    if (selectedDrug === '') {
      // console.log('No selectedDrug; no API call necessary');
      if (request) {
        console.log("Pre-resolve:", request);
        Promise.resolve(request)
          .then(() => {
            handleDrugChange('', [], '');
            console.log("Post-resolve:", request);
          });
      } else {
        handleDrugChange('', [], '');
      }
    } else {
      var api_call = '/api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=' + numResults + '&drugs=' + selectedDrug;
      console.log('apicall', api_call);

      axios({
        method: 'GET',
        url: api_call
      })
        .then((j) => {
          j = j.data;
          outcomeOptions = j["results"][0]["topOutcomes"];
          console.log("outcomeOptions", outcomeOptions);
          handleDrugChange(selectedDrug, outcomeOptions, '')
        }).catch((ex) => {
          // console.log('No outcomes found', ex);
          // console.log("INFO: selectedDrug:");
          // console.log(selectedDrug);
          handleDrugChange('', [], selectedDrug);
        });
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
  
  handleDrugChange(newDrug, topOutcomes, drugHasNoModel) {
    let { drugChange, dateformat } = this.props;
    drugChange(newDrug, topOutcomes, drugHasNoModel)
    let title1, title2;
    if (drugHasNoModel !== '') {
      title1 = '';
      title2 = '';
    } else {
      title1 = "Select a drug and effect";
      title2 = '';
    }
    drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
  }

  render() {
    return (
      <div className="section select_container">
        <div className="drug_title">Drug</div>
        <Select name="selected-drugs" joinValues multi simpleValue
          value={this.props.value}
          placeholder="Select drug(s)..."
          noResultsText="Drug not found"
          options={this.props.options}
          onChange={this.apiTopOutcomes}/>
      </div>
    );
  }
}

const mapStateToProps = (state) => {
  let { HomeReducer } = state;
  let { numOutcomeResults, drugSelectBox } = HomeReducer;
  let { value, options } = drugSelectBox;
  console.log('value',value, options)
  return {
    numOutcomeResults,
    value,
    options
  };
};
  
const mapDispatchToProps = (dispatch) => {
  const { drugSelectBoxDrugChange, drugSelectBoxSetDrug } = HomeActions;
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