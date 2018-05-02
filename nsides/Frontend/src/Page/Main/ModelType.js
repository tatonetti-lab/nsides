import React from 'react';
import { drawTimeSeriesGraph } from '../../Helpers/graphing';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';

class ModelType extends React.Component {
  constructor (props) {
    super (props);
    this.state = {

    };
    this.handleChange = this.handleChange.bind(this);
    // this.handleClick = this.handleClick.bind(this);
  }

  handleChange (e) {
    let { selectedIndex, value } = e.target;
    let { drugEffectModels } = this.props;
    // console.log(e.target.value)
    // console.log(selectedIndex, value, this.props.drugEffectModels);
    if (selectedIndex !== undefined) {
      let modelData = drugEffectModels[selectedIndex];
      let title1 = "Proportional Reporting Ratio over time";
      let title2 = "Number of reports by year";
      drawTimeSeriesGraph(modelData.estimates, modelData.nreports, title1, title2, '%Y', false, modelData.model);
    }
  }

  // handleClick (e) {
  //   e.preventDefault();
  //   e.target.parentNode.value = e.target.value;
  // }

  render () {
    let { selectedModel, drugEffectModels } = this.props;
    // console.log(this.props);
    // console.log('data', data);
    if (drugEffectModels.length === 0 || selectedModel === null) {
      return null;
    }
    let options = drugEffectModels.map((dataset, i) => {
      return <option key={i} 
              value={dataset.model}>
              {dataset.model}
            </option>;
    })
    return (
    <div className='standardStyle center'>
      Model Options: 
      <select className='model-types' onChange={this.handleChange}>
        {options}
      </select>
    </div>
    )
  }
}

const mapStateToProps = (state) => {
  const { drugEffectModels } = state.HomeReducer;
  return {
    drugEffectModels
  };
};
  
const mapDispatchToProps = (dispatch) => {
  return {};
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(ModelType));