import React from 'react';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { setdrugEffectModels } from '../../Redux/Actions/HomeActions';
import { drawTimeSeriesGraph } from '../../Helpers/graphTools/graphing';
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
      // dateformat: '%Y',
      // request: null,
      // drugs: '',
      // outcome: '',
      // numOutcomeResults: 'all',
      // outcomeOptions: [],
      // submitNewModelOption: ''
    };
    // this.handleDrugChange = this.handleDrugChange.bind(this);
    // this.handleDrugOutcomeChange = this.handleDrugOutcomeChange.bind(this);
  }

  componentDidMount () {
    let { dateformat } = this.state;
    drawTimeSeriesGraph([], [], "Select a drug and effect", "", dateformat, true);
  }

  render () {
    // console.log('rendering', this.state);

    return <div id='content'>
      {/* <Header/> */}
      <div id='selection'>
        <div className='select-row'>
          <div className='drug-effect-boxes standardStyle'>
            <DrugSelectBox
              // numOutcomeResults={this.state.numOutcomeResults}
              // onDrugChange={(newDrug, topOutcomes, drugHasNoModel) => this.handleDrugChange(newDrug, topOutcomes, drugHasNoModel)}
            />
            <EffectSelectBox
              // outcomeOptions={this.state.outcomeOptions}
              // outcome={this.state.outcome}
              // selectedDrug={this.state.drugs}
              // onDrugOutcomeChange={(newDrug, newOutcome) => this.handleDrugOutcomeChange(newDrug, newOutcome)}
            />
          </div>
          {/* <div>
            <ModelType/>
          </div> */}
        </div>
        {this.props.submitNewModelOption !== '' &&
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
  let  { drugEffectModels, submitNewModelOption } = state.HomeReducer;
  // console.log('drugEffectModels', drugEffectModels)
  return {
    drugEffectModels,
    submitNewModelOption
    // selectedModel
  };
};
  
const mapDispatchToProps = (dispatch) => { 
  return {
    setdrugEffectModels: (data) => {
      dispatch(setdrugEffectModels(data));
    },
    // setSelectedModel: (modelType) => {
    //   dispatch(setSelectedModel(modelType));
    // }
  };
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(Main));