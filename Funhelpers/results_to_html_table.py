

def results_to_html_table(results):
    if not results or not isinstance(results, list):
        return "<p>No data found.</p>"
    
    if isinstance(results[0],str):
        return results

    # Extract columns from keys of the first row dict
    columns = results[0].keys()
    
    table_html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    
    # Header row
    table_html += '<thead><tr>'
    for col in columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead>'
    
    # Data rows
    table_html += '<tbody>'
    for row in results:
        table_html += '<tr>'
        for col in columns:
            val = row[col]
            table_html += f'<td>{val if val is not None else ""}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    return table_html