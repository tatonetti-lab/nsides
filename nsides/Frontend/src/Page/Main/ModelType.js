import React from 'react';
import { drawTimeSeriesGraph } from '../../Helpers/graphTools/graphing';
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
      drawTimeSeriesGraph(modelData.estimates, modelData.nreports, title1, false, modelData.model);
    }
  }

  // handleClick (e) {
  //   e.preventDefault();
  //   e.target.parentNode.value = e.target.value;
  // }

  render () {
    let { selectedModel, drugEffectModels, effectSelectBoxValue } = this.props;
    // console.log(this.props);
    // console.log('data', data);
    if (drugEffectModels.length === 0 || selectedModel === null || effectSelectBoxValue === null) {
      return null;
    }


    let options = drugEffectModels.map((dataset, i) => {
      return <option key={i} 
              value={dataset.model}>
              {dataset.model}
            </option>;
    })
    return (
    <div className='model-types'>
      Model Options: 
      <select onChange={this.handleChange}>
        {options}
      </select>
    </div>
    )
  }
}

const mapStateToProps = (state) => {
  const { drugEffectModels, effectSelectBox } = state.HomeReducer;
  const { value } = effectSelectBox;
  return {
    drugEffectModels,
    effectSelectBoxValue: value
  };
};
  
const mapDispatchToProps = (dispatch) => {
  return {};
};

export default withRouter(connect(mapStateToProps, mapDispatchToProps)(ModelType));