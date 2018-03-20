class SubmitJobForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            options: drugs,
            value: []
        };

        // this.handleSubmit = this.handleSubmit.bind(this);
        this.handleSelectChange = this.handleSelectChange.bind(this);
        this.fetchDrugIndices = this.fetchDrugIndices.bind(this);
    }

    handleSelectChange(value) {
        this.setState({value}, () =>{
            this.fetchDrugIndices();
        });
    }

    fetchDrugIndices() {
        var selectedDrugs;
        var { request } = this.props.request;
        try {
            selectedDrugs = this.state.value;
        } catch (err) {
            selectedDrugs = [];
        }
        var indices;
        debug("selected drugs: ", selectedDrugs);

        if (selectedDrugs = []) {
            debug('No drug(s) selected; no API call necessary');
            if (request) {
                // debug("Pre-resolve: ", request);
                Promise.resolve(request).then(
                    function() {
                        debug("Post-resolve: ", request);
                    }.bind(this));
            } else {
                this.props.onDrug
            }
        }
    }

    /* handleSubmit(e) {
        console.log("The form was submitted: " + this.state.value);
        
        e.preventDefault();
        // Make request using SuperAgent
        //request.post('/jobsubmission')
        //    .type('form')
        //    .send({mtype: "LRC", model_index: this.state.value})
        //    .end(function(err, res) {
        //        if (err || !res.ok) {
        //            alert('Oh no! error');
        //        }
        //    });
    }

    onChangeModelType(e) {
        console.log("Model type: ", e);
    } */

    render() {
        return (
            <form className="form-signin form-submitjob" method="POST">
                <div className="form-group">
                    <div className="drug_title">Model type</div>
                    <select className="form-control" name="mtype">
                        <option value="dnn">DNN</option>
                        <option value="lrc">LRC</option>
                    </select>
                </div>
                <div className="form-group submit-select-container">
                    <div className="drug_title">Drug(s)</div>
                    <Select name="model_index" joinValues multi simpleValue
                        value={this.state.value}
                        placeholder="Select drug(s)..."
                        noResultsText="Drug(s) not found"
                        options={this.state.options}
                        onChange={this.handleSelectChange} />
                </div>
                <div className="form-group">
                    <input className="btn btn-lg btn-primary btn-block" type="submit" value="Submit job" />
                </div>
            </form>
        );
    }
}

ReactDOM.render(<SubmitJobForm />, document.getElementById("job_submit_container"))
