import os

#run this to update path to bundle.js in serve_pages.py
def setUpFor (code_type):
    serve_pages_file_header_lines = 6
    file_name = os.listdir('../Frontend/dist/bundles/' + code_type)[0]
    hashDictionary = {}
    hashDictionary[file_name[0]] = file_name[1]
    with open('./serve_pages.py','r') as f:
        code = f.readlines()
        f.close()
    start_line = "    resp = make_response(send_from_directory('../Frontend/dist/bundles/"
    end_line = '))\n'

    new_line = start_line + code_type + "', '" + file_name + "'" + end_line

    target1Index = 10 + serve_pages_file_header_lines   #index is one lower than actual line number (starts at 0)

    if code_type == 'prod':
        code[target1Index] = "    resp.headers['Content-Encoding'] = 'gzip'\n"
    elif code_type == 'dev':
        code[target1Index] = '\n'
    
    target2Index = 9 + serve_pages_file_header_lines
    if code[target2Index] != new_line:
        code[target2Index] = new_line
        with open('./serve_pages.py', 'w') as f:
            f.write(''.join(code))
            f.close()

if __name__ == "__main__":
	# app.run(debug=True, port=5000) #for testing
    environment_type = input('Enter environment type:')
    setUpFor(environment_type)