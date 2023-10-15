#PRINT PLAYER DATA FUNCTION
def print_player_data(f_name, l_name, d_birth, p_birth, s_birth, c_birth, sho, pos, hei, wei, col, d_team, d_round, d_pick, d_year, rs_stats_list, po_stats_list):
    print("\nPLAYER INFO:")
    print("\nFirst Name: " + f_name)
    print("Last Name: " + l_name)
    print("\nDate of Birth: " + d_birth)
    print("Place of Birth: " + p_birth)
    print("State of Birth: " + s_birth)
    print("Country of Birth: " + c_birth)
    print("\nShoots: " + sho)
    print("Position/s: " + ", ".join(pos))
    print("\nHeight: " + hei + " cm")
    print("Weight: " + wei + " kg")
    if col is not None:
        print("\nCollege: " + col)
    else:
        print("\nNo College")
    print("\nDRAFT")
    print("Team: " + d_team)
    print("Round: " + d_round)
    print("Pick: " + d_pick)
    print("Year: " + d_year)

    print("\n\nREGULAR SEASON STATS:")
    for e in rs_stats_list:
        print(f'\nYEAR {rs_stats_list.index(e) + 1}:')
        print("----------------------")
        for c, v in e.items():
            print(f'{c.upper()}: {v}')

    print("\n\nPLAYOFFS STATS:")
    for e in po_stats_list:
        print(f'\nYEAR {po_stats_list.index(e) + 1}:')
        print("----------------------")
        for c, v in e.items():
            print(f'{c.upper()}: {v}')

#PRINT PLAYER DATA FUNCTION
def print_teams_data(teams_list, teams_rings, teams_conference_division, teams_names):
    for t in teams_list:
        if t[1] == True:
            print(f'\n{t[0].upper()} - Rings: {teams_rings[t[0]]}, Conference: {teams_conference_division[t[0]]["Conf"]}, Division: {teams_conference_division[t[0]]["Div"]}')

    print('\n\n')
    
    for t, n in teams_names.items():
        print(f'{t.upper()}: {n}\n')