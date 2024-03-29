from pathlib import Path

import steamspypi


def get_mid_of_interval(interval_as_str):
    # Code copied from get_mid_of_interval() in create_dict_using_json.py in hidden-gems repository.
    interval_as_str_formatted = [
        s.replace(',', '') for s in interval_as_str.split('..')
    ]
    lower_bound = float(interval_as_str_formatted[0])
    upper_bound = float(interval_as_str_formatted[1])
    mid_value = (lower_bound + upper_bound) / 2

    return mid_value


def compute_ratio_players_vs_reviews(game, ratio_exponent=1, player_str='owners'):
    # Code copied from createLocalDictionary() in create_dict_using_json.py in hidden-gems repository.

    # Read data

    try:
        num_players = game[player_str]
        num_players = float(num_players)
    except KeyError:
        # NB: After SteamSpy's update, 'players_forever' is not provided and will lead to an error.
        num_players = None
    except ValueError:
        # NB: After SteamSpy's update, 'owners' is given as a range instead of a point-estimate.
        num_players = get_mid_of_interval(game[player_str])

    try:
        num_players_variance = game[player_str + '_variance']
    except KeyError:
        # NB: After SteamSpy's update, variance is not provided.
        num_players_variance = None

    num_positive_reviews = game["positive"]
    num_negative_reviews = game["negative"]

    # As per SteamSpy API documentation:
    #
    # * positive - number of positive user reviews
    # * negative - number of negative user reviews
    #
    # * owners - owners of this application on Steam. **Beware of free weekends!**
    # * owners_variance - variance in owners. The real number of owners lies in [owners +/- owners_variance] range.
    #
    # * players_forever - people that have played this game since March 2009.
    # * players_forever_variance - variance for total players.

    # Compute ratio
    num_reviews = num_positive_reviews + num_negative_reviews

    # Discard data with:
    # - more noise than signal,
    # - zero player (due to the use of a "lower or equal" sign),
    # - fewer players than reviews (a sign that data is spurious),
    # - zero review. Game is weird: either a development toolkit, or it was removed from the store, etc.
    if (
        (num_players_variance is not None and (num_players <= num_players_variance))
        or (num_players < num_reviews)
        or (num_reviews == 0)
    ):
        ratio_players_vs_reviews = -1
    else:
        if not (num_players > 0):
            raise AssertionError
        if not (num_reviews > 0):
            raise AssertionError

        ratio_players_vs_reviews = pow(num_players / num_reviews, ratio_exponent)

    return ratio_players_vs_reviews


def rank_games_based_on_ratio_players_vs_reviews(
    steamspy_data,
    ratio_exponent=1,
    player_str='owners',
):
    # Code copied from rankGames() in compute_stats.py in hidden-gems repository.

    # Sort data based on ratio
    appid_ranking = sorted(
        steamspy_data.keys(),
        key=lambda appid: compute_ratio_players_vs_reviews(
            steamspy_data[appid],
            ratio_exponent,
            player_str,
        ),
        reverse=True,
    )

    # Get game names
    game_name_ranking = [steamspy_data[appid]['name'] for appid in appid_ranking]

    # The following call to list() allows to copy the ranking, e.g. to compute its length before iterating over it.
    ranking = list(zip(appid_ranking, game_name_ranking, strict=True))

    return ranking


def print_ranking_to_file_stream(
    ranking,
    outfile=None,
    num_top_games_to_print=None,
    width=40,
):
    # Code copied from saveRankingToFile() in compute_stats.py in hidden-gems repository.

    from math import ceil, log10

    base_steam_store_url = "https://store.steampowered.com/app/"

    num_games = len(ranking)
    if num_top_games_to_print is not None:
        num_games = min(num_games, num_top_games_to_print)
    rank_width = ceil(log10(num_games))
    rank_format_str = '{:0' + str(rank_width) + '}'

    for iter_no, game_info in enumerate(ranking):
        current_rank = iter_no + 1
        (appid, game_name) = game_info

        store_url = base_steam_store_url + appid
        store_url_fixed_width = f'{store_url: <{width}}'

        sentence = (
            rank_format_str.format(current_rank)
            + ".\t["
            + game_name
            + "]("
            + store_url_fixed_width
            + ")"
        )

        if outfile is None:
            print(sentence)
        else:
            print(sentence, file=outfile)

        if (
            num_top_games_to_print is not None
            and current_rank == num_top_games_to_print
        ):
            break

    return


def print_ranking_to_file(ranking, output_filename=None, num_top_games_to_print=None):
    # Save the ranking to the output text file (if provided) in a format recognized by Github Gist.
    # Otherwise print the ranking to the screen

    if output_filename is None:
        print_ranking_to_file_stream(ranking, None, num_top_games_to_print)
    else:
        with Path(output_filename).open('w', encoding="utf8") as outfile:
            print_ranking_to_file_stream(ranking, outfile, num_top_games_to_print)

    return


def check_meta_data(data, ranking, num_top_games_to_print=10):
    print()

    for iter_no, game_info in enumerate(ranking):
        if iter_no == num_top_games_to_print:
            break

        (appid, _) = game_info
        print(data[appid])

    return


def main():
    # Ranking parameter
    ratio_exponent = -1
    player_str = 'owners'  # Either 'players_forever' or 'owners'
    # NB: After SteamSpy's update, only 'owners' is provided. Choosing 'players_forever' will lead to an error.

    # A ranking will be stored in the following text file
    output_filename = None  # "ranking.md"

    # Display parameter
    num_top_games_to_print = 25
    verbose = True

    data = steamspypi.load()

    ranking = rank_games_based_on_ratio_players_vs_reviews(
        data,
        ratio_exponent,
        player_str,
    )

    print_ranking_to_file(ranking, output_filename, num_top_games_to_print)

    if verbose:
        check_meta_data(data, ranking, num_top_games_to_print)

    return True


if __name__ == "__main__":
    main()
