function out = escape_bad_json( in )
out = strrep( in, '": Infinity', '": "Infinity"' );
