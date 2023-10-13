import psycopg2
from dicts.positions_dict import positions_dict
from scrap_player import generate_player_data

def insert_player_data(url):

    #GET PLAYER DATA
    player_data = generate_player_data(url)

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
                
                #INSERT PLAYER NAME
                insert_player_script    =   '''
                                            INSERT INTO players (first_name, last_name)
                                            VALUES (%s, %s) RETURNING id
                                            '''
                insert_player_values    =   (player_data['First Name'], player_data['Last Name'])
                cur.execute(insert_player_script, insert_player_values)
                #GET ID
                p_id = cur.fetchone()
                
                #INSERT PLAYER BIRTH INFO
                insert_p_bi_script      =   '''
                                            INSERT INTO player_birth_info
                                            (player_id,date_of_birth, place_of_birth, state_of_birth, country_of_birth)
                                            VALUES (%s, %s, %s, %s, %s)
                                            '''
                insert_p_bi_values      =   (p_id,
                                            player_data['Data of Birth'],
                                            player_data['Place of Birth'],
                                            player_data['State of Birth'],
                                            player_data['Country of Birth'])
                cur.execute(insert_p_bi_script, insert_p_bi_values)

                #INSERT PLAYER SHOOTS
                insert_p_s_script       =   '''
                                            INSERT INTO player_shoots(player_id, shoots)
                                            VALUES (%s, %s)
                                            '''
                insert_p_s_values       =   (p_id, player_data['Shoots'])
                cur.execute(insert_p_s_script, insert_p_s_values)

                #INSERT PLAYER POSITIONS
                for position in player_data['Positions']:
                    insert_p_p_script   =   '''
                                            INSERT INTO player_positions (player_id, position)
                                            VALUES (%s, %s)
                                            '''
                    insert_p_p_values   =   (p_id, positions_dict[position])
                    cur.execute(insert_p_p_script, insert_p_p_values)

                #INSERT PLAYER PHYSICAL INFO
                insert_p_pi_script      =   '''
                                            INSERT INTO player_physical_info (player_id, height_cm, weight_kg)
                                            VALUES (%s, %s, %s)
                                            '''
                insert_p_pi_values      =   (p_id, player_data['Height'], player_data['Weight'])
                cur.execute(insert_p_pi_script, insert_p_pi_values)

                #INSERT PLAYER COLLEGE
                insert_p_c_script       =   '''
                                            INSERT INTO player_college (player_id, college)
                                            VALUES (%s, %s)
                                            '''
                insert_p_c_values       =   (p_id, player_data['College'])
                cur.execute(insert_p_c_script, insert_p_c_values)
                
                #SELECT DRAFT TEAM ID
                select_d_t_script       =   '''
                                            SELECT id FROM teams
                                            WHERE team = %s
                                            '''
                select_d_t_values       =   (player_data['Draft Team'],)
                cur.execute(select_d_t_script, select_d_t_values)
                #GET DRAFT TEAM ID
                dt_id = cur.fetchone()
                
                #INSERT DRAFT
                insert_draft_script     =   '''
                                            INSERT INTO drafts (player_id, team_id, round, pick, year)
                                            VALUES (%s, %s, %s, %s, %s)
                                            '''
                insert_draft_values     =   (p_id,
                                            dt_id,
                                            player_data['Round'],
                                            player_data['Pick'],
                                            player_data['Draft Year'])
                cur.execute(insert_draft_script, insert_draft_values)

                #REGULAR SEASON STATS
                for stat in player_data['Regular Season Stats']:
                    
                    #SELECT TEAM ID
                    select_team_script  =   '''
                                            SELECT id FROM teams
                                            WHERE team = %s
                                            '''
                    select_team_values  =   (stat['Team'],)
                    cur.execute(select_team_script, select_team_values)
                    #GET TEAM ID
                    t_id = cur.fetchone()
                    
                    #INSERT REGULAR SEASON STATS
                    insert_stats_script =   '''
                                            INSERT INTO player_rs_stats
                                            (player_id, season, team_id,
                                            gp, gs, mp, fg, fga, fgp, tp, tpa, tpp, ft, fta, ftp, rb, ast, stl, blk, tov, pf, pts)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            '''
                    insert_stats_values =   (p_id,
                                            stat['Season'],
                                            t_id,
                                            stat['Games Played'],
                                            stat['Games Started'],
                                            stat['Minutes Played'],
                                            stat['Field Goals'],
                                            stat['Field Goal Attempts'],
                                            stat['Field Goal Percentage'],
                                            stat['Three Points'],
                                            stat['Three Point Attempts'],
                                            stat['Three Point Percentage'],
                                            stat['Free Throws'],
                                            stat['Free Throws Attempts'],
                                            stat['Free Throws Percentage'],
                                            stat['Rebounds'],
                                            stat['Assists'],
                                            stat['Steals'],
                                            stat['Blocks'],
                                            stat['Turnovers'],
                                            stat['Personal Fouls'],
                                            stat['Points'])
                    cur.execute(insert_stats_script, insert_stats_values)

                #PLAYOFFS STATS
                for stat in player_data['Playoffs Stats']:
                    
                    #SELECT TEAM ID
                    select_team_script  =   '''
                                            SELECT id FROM teams
                                            WHERE team = %s
                                            '''
                    select_team_values  =   (stat['Team'],)
                    cur.execute(select_team_script, select_team_values)
                    #GET TEAM ID
                    t_id = cur.fetchone()
                    
                    #INSERT PLAYOFFS STATS
                    insert_stats_script =   '''
                                            INSERT INTO player_po_stats
                                            (player_id, season, team_id,
                                            gp, gs, mp, fg, fga, fgp, tp, tpa, tpp, ft, fta, ftp, rb, ast, stl, blk, tov, pf, pts)
                                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                            '''
                    insert_stats_values =   (p_id,
                                            stat['Season'],
                                            t_id,
                                            stat['Games Played'],
                                            stat['Games Started'],
                                            stat['Minutes Played'],
                                            stat['Field Goals'],
                                            stat['Field Goal Attempts'],
                                            stat['Field Goal Percentage'],
                                            stat['Three Points'],
                                            stat['Three Point Attempts'],
                                            stat['Three Point Percentage'],
                                            stat['Free Throws'],
                                            stat['Free Throws Attempts'],
                                            stat['Free Throws Percentage'],
                                            stat['Rebounds'],
                                            stat['Assists'],
                                            stat['Steals'],
                                            stat['Blocks'],
                                            stat['Turnovers'],
                                            stat['Personal Fouls'],
                                            stat['Points'])
                    cur.execute(insert_stats_script, insert_stats_values)

    except Exception as error:
        print(error)

    finally:
        if conn is not None:
            conn.close()

