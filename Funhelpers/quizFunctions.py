from typing import Dict, List, Iterable, Tuple, Union, Set

# Question tuple:
# (uuid, q_numb, image_url, title, note, isMultiple, options)

def make_url(rel: str) -> str:
    # Simple passthrough or transform if you host under /static/images
    return f"/static/images/{rel}"

def getListOfQuestions(ano: int = 5):
    # uuid, q_numb, image, title, note, isMultipleChoice, list_of_answers
    list_of_questions = [
        (
            "bd415bce-6028-4a73-9273-295310b3f3b6",
            1,
            "anos/ano5/tema1/aula106/e1.png",
            "title-1",
            "note-1",
            False,
            ["Não sei", "700", "600", "620", "580"],
        ),
        (
            "a28eac48-a6e9-4b26-9840-08805e2a7a2d",
            2,
            "anos/ano5/tema1/aula106/e1.png",
            "title-2",
            "note-2",
            False,
            ["Não sei", "1400", "1450", "1250", "1427"],
        ),
        (
            "31019225-8336-45d4-825b-3cefd953984c",
            3,
            "anos/ano5/tema1/aula106/e1.png",
            "title-3",
            "note-3",
            False,
            ["Não sei", "1102", "1010", "1200", "1100"],
        ),
        (
            "c2fbaf7e-b689-44e6-b0e1-a76246019222",
            4,
            "anos/ano5/tema2/aula113/e5.png",
            "title-4",
            "note-4",
            False,
            ["Não sei","O João tem razão","A Joana tem razão"]
        ),
        (
            "4d72c744-2b85-4bc6-848c-9f60de652595",
            5,
            "anos/ano5/tema1/aula112/e3.png",
            "title-5",
            "note-5",
            True,
            ['Não sei','2^4','2^5','2^6','2^8']
        )
    ]
    out = []
    for uuid, qn, rel, title, note, isMultiple, opts in list_of_questions:
        img_url = make_url(rel)
        out.append((uuid, qn, img_url, title, note, isMultiple, opts))
    return out

def getPointsPerQuestions():
    # uuid, q_numb, list_of_points (aligned to options)
    list_of_points = [
        ("bd415bce-6028-4a73-9273-295310b3f3b6", 1, ["0", "-2", "5", "-2", "-2"]),
        ("a28eac48-a6e9-4b26-9840-08805e2a7a2d", 2, ["0", "5", "-2", "-2", "-2"]),
        ("31019225-8336-45d4-825b-3cefd953984c", 3, ["0", "-2", "-2", "-2", "5"]),
        ("c2fbaf7e-b689-44e6-b0e1-a76246019222", 4, ["0", "-3", "5"]),
        ("4d72c744-2b85-4bc6-848c-9f60de652595", 5, ["0", "-1", "5", "-1", "-1"])
    ]
    return list_of_points

# --- Scoring utilities ---

def _build_points_index() -> Dict[str, List[int]]:
    pts = {}
    for uuid, _qn, pts_list in getPointsPerQuestions():
        pts[uuid] = list(map(int, pts_list))
    return pts

def _build_options_index() -> Dict[str, List[str]]:
    idx = {}
    for uuid, _qn, _img, _title, _note, _is_multi, options in getListOfQuestions():
        idx[uuid] = options
    return idx

def _build_is_multi_index() -> Dict[str, bool]:
    idx = {}
    for uuid, _qn, _img, _title, _note, is_multi, _options in getListOfQuestions():
        idx[uuid] = is_multi
    return idx

def _build_qn_index() -> Dict[str, int]:
    idx = {}
    for uuid, qn, *_rest in getListOfQuestions():
        idx[uuid] = qn
    return idx

def _index_of(options: List[str], sel) -> int:
    if isinstance(sel, int):
        return sel if 0 <= sel < len(options) else -1
    if isinstance(sel, str):
        try:
            return options.index(sel)
        except ValueError:
            return -1
    return -1

def score_points_total(
    answers: Dict[Union[str, int], Union[int, str, Iterable[int], Iterable[str]]],
    questions: List[tuple]
) -> Dict[str, object]:
    """
    Sum per-option points for selections.
    answers may be keyed by q_numb or uuid; both are supported.
    """
    points_index = _build_points_index()
    options_index = _build_options_index()
    is_multi_index = _build_is_multi_index()
    qn_index = _build_qn_index()

    # Allow both qn and uuid keys in answers
    # Build a resolver mapping qn->uuid for quick lookup
    qn_to_uuid = {qn: uuid for uuid, qn, *_ in questions}

    total_points = 0
    per_question = {}

    for uuid, qn, _img, _title, _note, is_multi, options in questions:
        pts_for_opts = points_index.get(uuid)
        if not pts_for_opts or len(pts_for_opts) != len(options):
            per_question[uuid] = 0
            continue

        # resolve answer by uuid or qn
        sel = None
        if uuid in answers:
            sel = answers[uuid]
        elif qn in answers:
            sel = answers[qn]
        elif str(qn) in answers:
            sel = answers[str(qn)]

        if sel is None:
            per_question[uuid] = 0
            continue

        if is_multi:
            if isinstance(sel, (list, tuple, set)):
                idxs = {_index_of(options, s) for s in sel}
            else:
                idxs = {_index_of(options, sel)}
            valid = {i for i in idxs if i >= 0}
            q_points = sum(pts_for_opts[i] for i in valid)
        else:
            if isinstance(sel, (list, tuple, set)):
                # take first valid if a list was mistakenly sent
                idx = -1
                for s in sel:
                    i = _index_of(options, s)
                    if i >= 0:
                        idx = i
                        break
            else:
                idx = _index_of(options, sel)
            q_points = pts_for_opts[idx] if idx >= 0 else 0

        per_question[uuid] = q_points
        total_points += q_points

    return {"total_points": total_points, "per_question_points": per_question}

def score_counts(
    answers: Dict[Union[str, int], Union[int, str, Iterable[int], Iterable[str]]],
    questions: List[tuple]
) -> Dict[str, int]:
    """
    Count correct/wrong/skip using a simple convention:
    - Skip if no answer or the selected option(s) are empty or exactly ["Não sei"] or index 0 only.
    - Correct if the sum of selected points > 0 and no negative points were selected.
    - Wrong if selected but sum <= 0 or includes any negative points.
    This aligns with your per-option points model.
    """
    points_index = _build_points_index()

    correct = wrong = skip = 0
    total = len(questions)

    for uuid, qn, _img, _title, _note, is_multi, options in questions:
        pts_for_opts = points_index.get(uuid, [])
        # resolve answer
        sel = None
        if uuid in answers:
            sel = answers[uuid]
        elif qn in answers:
            sel = answers[qn]
        elif str(qn) in answers:
            sel = answers[str(qn)]

        # Normalize selection to list of indices
        if sel is None:
            skip += 1
            continue

        if is_multi:
            if isinstance(sel, (list, tuple, set)):
                idxs = {_index_of(options, s) for s in sel}
            else:
                idxs = {_index_of(options, sel)}
            idxs = [i for i in idxs if i >= 0]
        else:
            if isinstance(sel, (list, tuple, set)):
                idx = -1
                for s in sel:
                    i = _index_of(options, s)
                    if i >= 0:
                        idx = i
                        break
            else:
                idx = _index_of(options, sel)
            idxs = [idx] if idx >= 0 else []

        if not idxs:
            skip += 1
            continue

        # Treat choosing only the "Não sei" (index 0) as skip
        if len(idxs) == 1 and idxs[0] == 0:
            skip += 1
            continue

        pts = [pts_for_opts[i] if 0 <= i < len(pts_for_opts) else 0 for i in idxs]
        sum_pts = sum(pts)
        any_neg = any(p < 0 for p in pts)

        if sum_pts > 0 and not any_neg:
            correct += 1
        else:
            wrong += 1

    return {"total": total, "correct": correct, "wrong": wrong, "skip": skip}
