// nSides DrugSelectBox, Updated July 2017

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
class DrugSelectBox extends React.Component {
    displayName: 'DrugSelectBox';
    constructor(props) {
        super(props);
        this.handleSelectChange = this.handleSelectChange.bind(this);
        this.apiTopOutcomes = this.apiTopOutcomes.bind(this);
        this.state = {
            options: drugs,
            value: '', //[],
            // numOutcomeResults: this.props.numOutcomeResults
        };
    }

    handleSelectChange(value) {
        this.setState({ value }, () => {
            this.apiTopOutcomes();
        });
    }

    apiTopOutcomes() {
        var selectedDrug; // = this.state.value['value'];
        try {
            //selectedDrug = this.state.value['value'];
            selectedDrug = this.state.value;
        } catch (err) {
            selectedDrug = '';
        }
        var numResults = this.props.numOutcomeResults;
        var outcomeOptions;
        debug("selectedDrug", selectedDrug, "numResults", numResults)

        if (selectedDrug == '') {
            debug('No selectedDrug; no API call necessary');
            if (request) {
                debug("Pre-resolve:", request);
                Promise.resolve(request)
                    .then(function () {
                        this.props.onDrugChange('', [], '');
                        debug("Post-resolve:", request);
                    }.bind(this));
            } else {
                this.props.onDrugChange('', [], '');
            }
        }

        else {
            var api_call = '/api/v1/query?service=nsides&meta=topOutcomesForDrug&numResults=' + numResults + '&drugs=' + selectedDrug;
            debug(api_call);

            request = fetch(api_call) // http://stackoverflow.com/a/41059178
                .then(function (response) {
                    return response.json();
                })
                .then(function (j) {
                    outcomeOptions = j["results"][0]["topOutcomes"];
                    debug("outcomeOptions", outcomeOptions);
                    this.props.onDrugChange(selectedDrug, outcomeOptions, '')
                }.bind(this))
                .catch(function (ex) {
                    debug('No outcomes found', ex);
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
                    onChange={this.handleSelectChange} />
            </div>
        );
    }
}
