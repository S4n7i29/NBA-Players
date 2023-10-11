import psycopg2
from scrap_teams import generate_teams_data

def insert_teams_data():

    #GET TEAMS DATA
    teams_list, teams_r_list, teams_c_d_list = generate_teams_data()

    #SET CONN PARAMETERS
    hostname = 'localhost'
    database = 'all_time_nba_players'
    username = 'postgres'
    pwd = 'POSTGREStati0209'
    port_id = 5432

    #CONNECTION
    conn = None
    try:
        with psycopg2.connect(
            host        = hostname,
            dbname      = database,
            user        = username,
            password    = pwd,
            port        = port_id
        ) as conn:

            with conn.cursor() as cur:                

                #INSERT TEAMS
                for t in teams_list:
                    
                    #INSERT TEAM NAME
                    insert_team_script = 'INSERT INTO teams (team) VALUES (%s) RETURNING id'
                    insert_team_values = (t,)
                    cur.execute(insert_team_script, insert_team_values)
                    #GET ID
                    t_id = cur.fetchone()

                    #INSERT TEAM RINGS
                    insert_t_r_script = 'INSERT INTO team_rings (team_id, rings) VALUES (%s, %s)'
                    insert_t_r_values = (t_id, teams_r_list[t])
                    cur.execute(insert_t_r_script, insert_t_r_values)

                    #INSERT TEAM CONFERENCE & DIVISION
                    insert_t_c_d_script = 'INSERT INTO team_conference_division (team_id, conference, division) VALUES (%s, %s, %s)'
                    insert_t_c_d_values = (t_id, teams_c_d_list[t]['Conf'], teams_c_d_list[t]['Div'])
                    cur.execute(insert_t_c_d_script, insert_t_c_d_values)

    except Exception as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

insert_teams_data()