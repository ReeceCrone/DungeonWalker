
from main import GridModel, PlayerModel

def test_grid_model_set_and_get():
    grid = GridModel(10, 10)

    grid.set_cell_color(2, 3, "grey")
    assert grid.get_cell_color(2, 3) == "grey"


def test_player_model_initial_position():
    player = PlayerModel()
    assert (player.row, player.col) == (0, 0)

def test_player_model_move():
    player = PlayerModel()
    player.update_position(3, 4)
    assert (player.row, player.col) == (3, 4)

def main():
    test_grid_model_set_and_get()
    test_player_model_initial_position()
    test_player_model_move()
    print("All tests passed.")

if __name__ == "__main__":
    main()