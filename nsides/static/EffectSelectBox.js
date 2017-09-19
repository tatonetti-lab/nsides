// nSides EffectSelectBox, Updated July 2017

// Copyright (C) 2017, Tatonetti Lab
// Tal Lorberbaum <tal.lorberbaum@columbia.edu>
// Victor Nwankwo <vtn2106@cumc.columbia.edu>
// Joe Romano <dr2160@cumc.columbia.edu>
// Ram Vanguri <rami.vanguri@columbia.edu>
// Nicholas P. Tatonetti <nick.tatonetti@columbia.edu>
// All rights reserved.

// This site is released under a CC BY-NC-SA 4.0 license.
// For full license details see LICENSE.txt at 
// https://github.com/tatonetti-lab/nsides or go to:
// http://creativecommons.org/licenses/by-nc-sa/4.0/

var request = null;
class EffectSelectBox extends React.Component {
	displayName: 'EffectSelectBox';
	constructor (props) {
        super(props);
        this.handleSelectChange = this.handleSelectChange.bind(this);
		this.state = {
			options: this.props.outcomeOptions,
			value: this.props.outcome, //'', //[],
            // numOutcomeResults: this.props.numOutcomeResults
            // loadingIconStyle: {float:"right", display:"none"},
		};
	}

	handleSelectChange (value) {
//		debug('You\'ve selected:', value);    
        
		this.setState({ value }, () => {
            var selectedOutcome;
            try {
                selectedOutcome = this.state.value['value'];
            } catch(err) {
                selectedOutcome = '';
            }
            this.props.onDrugOutcomeChange(this.props.selectedDrug, selectedOutcome); 
        } );
	}

//	toggleDisabled (e) {
//		this.setState({ disabled: e.target.checked });
//	}
    
	render () {        
        return (
			<div className="section select_container_effect">
                <div className="effect_title">Effect</div>
				<Select name="selected-effect"
                 value={this.props.outcome} //{this.state.value}
                 placeholder="Select effect..."
                 noResultsText="No effects found" 
                 options={this.props.outcomeOptions}
                 onChange={this.handleSelectChange} />
			</div>
		);
	}
}