import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { setDrugEffectData } from '../../Redux/Actions/HomeAction';
import { drawTimeSeriesGraph } from '../../Helpers/graphing';
import DrugSelectBox from './DrugSelectBox';
import EffectSelectBox from './EffectSelectBox';
import SubmitModelButton from './SubmitModelButton';
import Header from '../../Header';
import ModelType from './ModelType';
// import axios from 'axios';
// import Actions from '../../Redux/Actions/Actions';

class Main extends React.Component {
  constructor (props) {
    super (props);
    this.state = {
      dateformat: '%Y',
      request: null,
      drugs: '',
      outcome: '',
      numOutcomeResults: 'all',
      outcomeOptions: [],
      submitNewModelOption: ''
    };
    this.handleDrugChange = this.handleDrugChange.bind(this);
    this.handleDrugOutcomeChange = this.handleDrugOutcomeChange.bind(this);
  }

  componentDidMount () {
    let { dateformat } = this.state;
    drawTimeSeriesGraph([], [], "Select a drug and effect", "", dateformat, true);
  }

  handleDrugChange(newDrug, topOutcomes, drugHasNoModel) {
    let { dateformat } = this.state;
    // console.log('newDrug:', newDrug);
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
      drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
    });
  }

  handleDrugOutcomeChange(newDrug, newOutcome) {
    this.setState({
      drugs: newDrug,
      outcome: newOutcome
    }, () => {
      let { request, dateformat } = this.state;
      let title1, title2;
      console.log("newDrug", newDrug, "newOutcome", newOutcome, this);
      
      if ((newDrug === "") || (newOutcome === "")) {
        if (this.state.submitNewModelOption !== '') {
          title1 = "";
          title2 = '';
        } else {
          title1 = "Select a drug and effect";
          title2 = '';
        }
        drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
      } else {
        var api_call = "/api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs=" + newDrug + "&outcome=" + newOutcome;
        // console.log(api_call);
        request = fetch(api_call) // http://stackoverflow.com/a/41059178
          .then(function (response) {
            return response.json();
          })
          .then(function (j) {
            let { setDrugEffectData } = this.props;
            // console.log("data:");
            console.log('received', j, '\n');
            var data, data2, modelType;// hasModelType = false, foundIndex;
            modelType = j.results[0].model;
            data = j["results"][0]["estimates"];
            data2 = j["results"][0]["nreports"];
            // if (selectedModel !== null) {
            //   for (var i = 0; i < j.results.length; i++) {
            //     if (j.results[i].model === selectedModel) {
            //       hasModelType = true;
            //       foundIndex = i;
            //       break;
            //     }
            //   }
            // }
            // console.log('has modeltype',hasModelType)
            // if (hasModelType) {
            //   modelType = selectedModel;
            //   data = j.results[foundIndex].estimates;
            //   data2 = j.results[foundIndex].nreports;
            // } else {
            //   modelType = j.results[0].model;
            //   data = j["results"][0]["estimates"];
            //   data2 = j["results"][0]["nreports"];
            //   setSelectedModel(modelType);
            // }
            // console.log('data', data, 'data2', data2);
            // console.log("modelType: ", modelType);
            // console.log("drug-effect data", data);
            // console.log("number of reports by year", data2);

            /* Set variables */
            var data1 = data;
            var title1 = "Proportional Reporting Ratio over time";
            var title2 = "Number of reports by year";
            // console.log('modelType', modelType)
            // setSelectedModel(modelType);
            // let select = document.querySelector(`select.model-types`);
            // if (select !== null) {
            //   select.value = modelType;
            // }
            setDrugEffectData(j.results);
            drawTimeSeriesGraph(data1, data2, title1, title2, dateformat, false, modelType);
          }.bind(this))
          // .catch(function (ex) {
          //   // console.log('Parsing failed', ex);
          //   request = null;
          //   var title1 = "Select a drug and effect"; //"No results found";
          //   var title2 = '';
          //   console.log('hi',ex)
          //   drawTimeSeriesGraph([], [], title1, title2, dateformat, true);
          // });
      }
    });

    
  }

  render () {
    // console.log('rendering', this.state);
    return <div id='content'>
      {/* <Header/> */}
      <div id='selection'>
        <div className='select-row'>
          <div className='drug-effect-boxes standardStyle'>
            <DrugSelectBox
              numOutcomeResults={this.state.numOutcomeResults}
              onDrugChange={(newDrug, topOutcomes, drugHasNoModel) => this.handleDrugChange(newDrug, topOutcomes, drugHasNoModel)}
            />
            <EffectSelectBox
              outcomeOptions={this.state.outcomeOptions}
              outcome={this.state.outcome}
              selectedDrug={this.state.drugs}
              onDrugOutcomeChange={(newDrug, newOutcome) => this.handleDrugOutcomeChange(newDrug, newOutcome)}
            />
          </div>
          <div>
            <ModelType 
              drugEffectData={this.props.drugEffectData}/>
          </div>
        </div>
        {this.state.submitNewModelOption !== '' &&
          <div className="newModelNotification">
            <p>We have not yet generated a model for this drug / drug combination.</p>
            <p>If you would like to submit this drug for computation, click on the following button:</p>
            <SubmitModelButton
              drugName={this.state.submitNewModelOption}
            />
            <p><i>Note: this will redirect you to an external page for authentication if you are not already logged in.</i></p>
          </div>
        }
      </div>
      <section className="select_bar">
        <div id="viz_container">
        </div>
      </section>
    </div>;
  }
}

const mapStateToProps = (state) => {
  let  { drugEffectData } = state.HomeReducer;
  console.log('drugEffectData', drugEffectData)
  return {
    drugEffectData,
    // selectedModel
  };
};
  
const mapDispatchToProps = (dispatch) => { 
  return {
    setDrugEffectData: (data) => {
      dispatch(setDrugEffectData(data));
    },
    // setSelectedModel: (modelType) => {
    //   dispatch(setSelectedModel(modelType));
    // }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Main));