class SubmitJobForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            options: drugs,
            value: []
        };

        this.handleSubmit = this.handleSubmit.bind(this);
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
                debug("Pre-resolve: ", request);
                Promise.resolve(request).then(
                    function() {
                        debug("Post-resolve: ", request);
                    }.bind(this));
            } else {
                this.props.onDrug
            }
        }
    }

    handleSubmit(e) {
        console.log("The form was submitted: " + this.state.value);
        e.preventDefault();
    }

    render() {
        return (
            <form onSubmit={this.handleSubmit} className="form-signin form-submitjob">
                <div className="form-group">
                    <div className="drug_title">Model type</div>
                    <select className="form-control">
                        <option value="dnn">DNN</option>
                        <option value="lrc">LRC</option>
                    </select>
                </div>
                <div className="form-group submit-select-container">
                    <div className="drug_title">Drug(s)</div>
                    <Select name="selected-drugs" joinValues multi simpleValue
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
