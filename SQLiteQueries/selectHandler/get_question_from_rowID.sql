SELECT 
    r.rowid,
    t.ano,
    t.nome_tema,
    a.title as aula_title,
    a.num_tema,
    a.num_aula,
    r.uuid,
    r.imagem,
    r.type_of_problem,
    (r.type_of_selection = 'multiple_choice') as is_multiple_choice,
    r.question_number,
    r.formatting,
    r.possible_answers,
    r.correct_answer,
    r.scoring_system,
    r.titulo,
    r.nota
FROM responses r
JOIN aulas a ON a.num_aula = r.aula 
JOIN temas t ON t.num_tema = a.num_tema AND t.ano = a.ano
WHERE r.rowid = ?