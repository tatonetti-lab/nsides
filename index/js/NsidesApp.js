// nSides App, Updated July 2017

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

class NsidesApp extends React.Component {
    constructor(props) {
    super(props);
        this.state = {drugs: '',
                      outcome: '',
                      numOutcomeResults: 10,
                      outcomeOptions: []};
                    // plotWidth: window.innerWidth < 625 ? (window.innerWidth-50) : 625,
                    // plotHeight: 350};
    }

    render() {
        return <div>
               <div className='select-row'>
               <section>
               <DrugSelectBox
                      numOutcomeResults={this.state.numOutcomeResults}
                      onDrugChange={(newDrug,topOutcomes) => this.handleDrugChange(newDrug,topOutcomes)}
               />
               <EffectSelectBox
                      outcomeOptions={this.state.outcomeOptions}
                      outcome={this.state.outcome}
                      selectedDrug={this.state.drugs}
                      onDrugOutcomeChange={(newDrug,newOutcome) => this.handleDrugOutcomeChange(newDrug,newOutcome)}
               />
               </section>
               </div>
               </div>;
    }

    handleDrugChange(newDrug,topOutcomes) {      
        this.setState({ drugs: newDrug,
                        outcome: '',
                        outcomeOptions: topOutcomes}, () => {
          debug('drug updated');
          title1 = "Select a drug and effect";
          drawTimeSeriesGraph([],title1,dateformat,blank=true);
        });
    }

    handleDrugOutcomeChange(newDrug,newOutcome) {
        this.setState({ drugs: newDrug,
                        outcome: newOutcome}, () => {
            debug("newDrug", newDrug, "newOutcome", newOutcome)
            if ( (newDrug == "") || (newOutcome == "") ) {
                title1 = "Select a drug and effect";
                drawTimeSeriesGraph([],title1,dateformat,blank=true);
            }

            else {
                // Fetch from nsides API
                var api_call = "/api/v1/query?service=nsides&meta=estimateForDrug_Outcome&drugs="+newDrug+"&outcome="+newOutcome;

                request = fetch(api_call) // http://stackoverflow.com/a/41059178
                           .then(function(response) {
                               // Convert to JSON
                               // debug("response", response)
                               return response.json();
                           })
                           .then(function(j) {
                               var data = j["results"][0]["estimates"];
                               debug("drug-effect data", data);

                               /* Set variables */
                               var data1 = data;
                               var title1 = "Proportional Reporting Ratio over time";
                               drawTimeSeriesGraph(data1,title1,dateformat);
                           })
                           .catch(function(ex) {
                               debug('Parsing failed', ex);
                               request = null;
                               var title1 = "Select a drug and effect"; //"No results found";
                               drawTimeSeriesGraph([],title1,dateformat,blank=true);
                           })

            }
        });
    }

}

ReactDOM.render(<NsidesApp/>, document.getElementById("container"))