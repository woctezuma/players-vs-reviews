def compute_ratio_players_vs_reviews(game, ratio_exponent=1):
    # Code copied from createLocalDictionary() in create_dict_using_json.py in hidden-gems repository.

    # Read data
    num_players = game['players_forever']
    num_positive_reviews = game["positive"]
    num_negative_reviews = game["negative"]

    # Compute ratio
    num_reviews = num_positive_reviews + num_negative_reviews

    try:
        ratio_players_vs_reviews = pow(num_players / num_reviews, ratio_exponent)
    except ZeroDivisionError:
        ratio_players_vs_reviews = -1

    return ratio_players_vs_reviews


def rank_games_based_on_ratio_players_vs_reviews(steamspy_data, ratio_exponent=1):
    # Code copied from rankGames() in compute_stats.py in hidden-gems repository.

    # Sort data based on ratio
    appID_ranking = sorted(steamspy_data.keys(),
                           key=lambda appID: compute_ratio_players_vs_reviews(steamspy_data[appID], ratio_exponent),
                           reverse=True)

    # Get game names
    game_name_ranking = list(map(lambda appID: steamspy_data[appID]['name'], appID_ranking))

    # The following call to list() allows to copy the ranking, e.g. to compute its length before iterating over it.
    ranking = list(zip(appID_ranking, game_name_ranking))

    return ranking


def print_ranking_to_file_stream(ranking, outfile=None, num_top_games_to_print=None, width=40):
    # Code copied from saveRankingToFile() in compute_stats.py in hidden-gems repository.

    from math import log10, ceil

    base_steam_store_url = "http://store.steampowered.com/app/"

    num_games = len(ranking)
    if num_top_games_to_print is not None:
        num_games = min(num_games, num_top_games_to_print)
    rank_width = ceil(log10(num_games))
    rank_format_str = '{:0' + str(rank_width) + '}'

    for (iter_no, game_info) in enumerate(ranking):
        current_rank = iter_no + 1
        (appid, game_name) = game_info

        store_url = base_steam_store_url + appid
        store_url_fixed_width = f'{store_url: <{width}}'

        sentence = rank_format_str.format(current_rank) + ".\t[" + game_name + "](" + store_url_fixed_width + ")"

        if outfile is None:
            print(sentence)
        else:
            print(sentence, file=outfile)

        if num_top_games_to_print is not None and current_rank == num_top_games_to_print:
            break

    return


def print_ranking_to_file(ranking, output_filename=None, num_top_games_to_print=None):
    # Save the ranking to the output text file (if provided) in a format parsable by Github Gist.
    # Otherwise print the ranking to the screen

    if output_filename is None:
        print_ranking_to_file_stream(ranking, None, num_top_games_to_print)
    else:
        with open(output_filename, 'w', encoding="utf8") as outfile:
            print_ranking_to_file_stream(ranking, outfile, num_top_games_to_print)

    return


def check_meta_data(data, ranking, num_top_games_to_print=10):
    for (iter_no, game_info) in enumerate(ranking):

        if iter_no > num_top_games_to_print:
            break

        (appid, game_name) = game_info
        print(data[appid])

    return


if __name__ == "__main__":
    from download_json import getTodaysSteamSpyData

    # Ranking parameter
    ratio_exponent = -1
    # A ranking will be stored in the following text file
    output_filename = None  # "ranking.md"
    # Display parameter
    num_top_games_to_print = 10
    verbose = True

    data = getTodaysSteamSpyData()

    ranking = rank_games_based_on_ratio_players_vs_reviews(data, ratio_exponent)

    print_ranking_to_file(ranking, output_filename, num_top_games_to_print)

    if verbose:
        check_meta_data(data, ranking, num_top_games_to_print=10)
