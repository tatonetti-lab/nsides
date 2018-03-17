import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import Header from './Header';
import DrugSelectBox from './DrugSelectBox';
import EffectSelectBox from './EffectSelectBox';
import SubmitModelButton from './SubmitModelButton';
import '../../css/main.css';
// import axios from 'axios';
// import Actions from '../../Redux/Actions/Actions';

class Main extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    }
  }
  handleDrugChange(newDrug, topOutcomes, drugHasNoModel) {
    console.log('newDrug:', newDrug);
    this.setState({
      drugs: newDrug,
      outcome: '',
      submitNewModelOption: drugHasNoModel,
      outcomeOptions: topOutcomes
    }, () => {
      let title1, title2;
      if (this.state.submitNewModelOption !== '') {
        title1 = '';
        title2 = '';
      } else {
        title1 = "Select a drug and effect";
        title2 = '';
      }
      drawTimeSeriesGraph([], [], title1, title2, dateformat, blank = true);
    });
  }

  handleDrugOutcomeChange(newDrug, newOutcome) {
      this.setState({
          drugs: newDrug,
          outcome: newOutcome
      }, () => {
          debug("newDrug", newDrug, "newOutcome", newOutcome)
          if ((newDrug == "") || (newOutcome == "")) {
              if (this.state.submitNewModelOption !== '') {
                  title1 = "";
                  title2 = '';
              } else {
                  title1 = "Select a drug and effect";
                  title2 = '';
              }
              drawTimeSeriesGraph([], [], title1, title2, dateformat, blank = true);
          }

          else {
              var api_call = "/api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs=" + newDrug + "&outcome=" + newOutcome;
              console.log(api_call);

              request = fetch(api_call) // http://stackoverflow.com/a/41059178
                  .then(function (response) {
                      return response.json();
                  })
                  .then(function (j) {
                      console.log("data:");
                      console.log(j);
                      var data = j["results"][0]["estimates"];
                      var data2 = j["results"][0]["nreports"];
                      var modelType = j["results"][0]["model"]
                      debug("modelType: ", modelType);
                      // debug("drug-effect data", data);
                      // debug("number of reports by year", data2);

                      /* Set variables */
                      var data1 = data;
                      var title1 = "Proportional Reporting Ratio over time";
                      var title2 = "Number of reports by year";
                      drawTimeSeriesGraph(data1, data2, title1, title2, dateformat, blank = false, modelType = modelType);
                  })
                  .catch(function (ex) {
                      debug('Parsing failed', ex);
                      request = null;
                      var title1 = "Select a drug and effect"; //"No results found";
                      var title2 = '';
                      drawTimeSeriesGraph([], [], title1, title2, dateformat, blank = true);
                  })

          }
      });
  }

  render () {
    return <div id='content'>
      <Header/>
      <div>
        <div className='select-row'>
          <section>
            <DrugSelectBox
              numOutcomeResults={this.state.numOutcomeResults}
              onDrugChange={(newDrug, topOutcomes, drugHasNoModel) => this.handleDrugChange(newDrug, topOutcomes, drugHasNoModel)}
            />
            {/* <EffectSelectBox
              outcomeOptions={this.state.outcomeOptions}
              outcome={this.state.outcome}
              selectedDrug={this.state.drugs}
              onDrugOutcomeChange={(newDrug, newOutcome) => this.handleDrugOutcomeChange(newDrug, newOutcome)}
            /> */}
          </section>
        </div>
        {/* {this.state.submitNewModelOption !== '' &&
          <div className="newModelNotification">
            <p>We have not yet generated a model for this drug / drug combination.</p>
            <p>If you would like to submit this drug for computation, click on the following button:</p>
            <SubmitModelButton
                drugName={this.state.submitNewModelOption}
            />
            <p><i>Note: this will redirect you to an external page for authentication if you are not already logged in.</i></p>
          </div>
        } */}
      </div>;
    </div>;
  }
}

const mapStateToProps = (state) => {
  return {};
};
  
const mapDispatchToProps = (dispatch) => {
  return {};
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Main));