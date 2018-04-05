import React from 'react';
import drugs from './drugs-top-200';
import Select from 'react-select';
import '../../css/react-select.css';

var request = null;
class DrugSelectBox extends React.Component {
  constructor(props) {
    super(props);
    this.handleSelectChange = this.handleSelectChange.bind(this);
    this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
    this.state = {
      options: drugs,
      value: '', //[],
      request: null
    };
  }

  handleSelectChange(value) {
    this.setState({ value }, () => {
      this.apiTopOutcomes();
    });
  }

  apiTopOutcomes() {
    var selectedDrug;
    try {
      // react-select doesn't sort values. Here, we sort them numerically.
      var selectedDrugArray = this.state.value.split(',').map(function(item) {
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
      console.log("Error! ", err);
      selectedDrug = '';
    }
    var numResults = this.props.numOutcomeResults;
    var outcomeOptions;

    console.log("selectedDrug", selectedDrug, "numResults", numResults);

    if (selectedDrug === '') {
      console.log('No selectedDrug; no API call necessary');
      if (request) {
        console.log("Pre-resolve:", request);
        Promise.resolve(request)
          .then(function () {
            this.props.onDrugChange('', [], '');
            console.log("Post-resolve:", request);
          }.bind(this));
      } else {
        this.props.onDrugChange('', [], '');
      }
    } else {
      var api_call = '/api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=' + numResults + '&drugs=' + selectedDrug;
      console.log('apicall', api_call);

      request = fetch(api_call)
        .then(function (response) {
          return response.json();
        }).then(function (j) {
          outcomeOptions = j["results"][0]["topOutcomes"];
          console.log("outcomeOptions", outcomeOptions);
          this.props.onDrugChange(selectedDrug, outcomeOptions, '')
        }.bind(this)).catch(function (ex) {
          console.log('No outcomes found', ex);
          request = null;
          console.log("INFO: selectedDrug:");
          console.log(selectedDrug);
          this.props.onDrugChange('', [], selectedDrug);
        }.bind(this))
    }
  }

  render() {
    return (
      <div className="section select_container">
        <div className="drug_title">Drug</div>
        <Select name="selected-drugs" joinValues multi simpleValue
          value={this.state.value}
          placeholder="Select drug(s)..."
          noResultsText="Drug not found"
          options={this.state.options}
          onChange={this.handleSelectChange}/>
      </div>
    );
  }
}

export default DrugSelectBox;