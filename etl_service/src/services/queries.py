def movies_query(offset: int) -> str:
    movies_query = f"""SELECT
                                        fw.id as fw_id, 
                                        fw.title, 
                                        fw.description, 
                                        fw.rating, 
                                        fw.filmwork_type, 
                                        fw.created, 
                                        fw.modified, 
                                        pfw.role, 
                                        p.id, 
                                        p.first_name,
                                        p.last_name,
                                        g.name,
                                        g.id as g_id
                                    FROM movies_filmwork fw
                                    LEFT JOIN movies_personrole pfw ON pfw.filmwork_id = fw.id
                                    LEFT JOIN movies_person p ON p.id = pfw.person_id
                                    LEFT JOIN movies_filmwork_genres gfw ON gfw.filmwork_id = fw.id
                                    LEFT JOIN movies_genre g ON g.id = gfw.genre_id
                                    ORDER BY fw.modified DESC
                                    LIMIT 100 
                                    OFFSET {offset};"""
    return movies_query


def genres_query(offset: int) -> str:
    genres_query = f"""SELECT
                                    g.name,
                                    g.id as g_id,
                                    fw.id as fw_id
                                    FROM movies_genre g
                                    LEFT JOIN movies_filmwork_genres gfw ON gfw.genre_id = g.id
                                    LEFT JOIN movies_filmwork fw ON fw.id = gfw.filmwork_id
                                    ORDER BY g.modified DESC
                                    LIMIT 100 
                                    OFFSET {offset};"""
    return genres_query


def persons_query(offset: int) -> str:
    persons_query = f"""SELECT
                                    p.first_name,
                                    p.last_name,
                                    p.id as p_id,
                                    fw.id as fw_id,
                                    pfw.role as person_role
                                    FROM movies_person p
                                    LEFT JOIN movies_personrole pfw ON pfw.person_id = p.id
                                    LEFT JOIN movies_filmwork fw ON fw.id = pfw.filmwork_id
                                    ORDER BY p.modified DESC
                                    LIMIT 100 
                                    OFFSET {offset};"""
    return persons_query
