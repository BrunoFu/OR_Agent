import re, random, copy, string
from typing import Any, Dict, Optional, Tuple, Union

import textarena as ta
from textarena.envs.WordSearch.renderer import create_board_str

import nltk
from nltk.corpus import words
nltk.download('words')

class WordSearchEnv(ta.Env):
    """ Word Search environment """

    def __init__(self, hardcore: Optional[bool] = False, max_turns: int = 20):
        super().__init__()
        self.hardcore = hardcore
        self.max_turns = max_turns
        self.num_words = 5
        self.num_incorrect_tries = 20
        self.word_list = words.words("en") if self.hardcore else words.words("en-basic")  ## load the word list

    def get_board_str(self):
        return create_board_str(game_state=self.state.game_state)

    def reset(self, num_players: int, seed: Optional[int] = None):
        self.state = ta.SinglePlayerState(num_players=num_players, seed=seed, max_turns=self.max_turns) ## initialise the game state
        self.game_board, self.placed_words = self._generate_word_search() ## load the game board
        game_state = {"board": copy.deepcopy(self.game_board), "rendered_board": self._render_board(self.game_board)}
        self.state.reset(game_state=game_state, player_prompt_function=self._generate_player_prompt)
        self._observe_current_state()

    def _generate_player_prompt(self, player_id: int, game_state: Dict[int, Any]) -> str:
        return (
            f"You are Player {player_id}, and you are participating in a Word Search challenge "
            f"modeled as {'Hardcore' if self.hardcore else 'Basic'}. The objective is to find and highlight hidden words "
            f"on the grid below. The rows and columns are numbered for your reference.\n\n"
            "Here is the current state of the Word Search board:\n"
            "----------------------------------------\n"
            "Words you have already found are marked in square brackets [ ]. Each row and column is numbered for clarity.\n"
            "\n\nTo locate a word, specify the row and column of its start and end letters. Note that words are either across or down.\n"
            "You may type your response and thoughts in any manner. But you may only submit one submission at a time. For your submissions, use the format '[start_row start_col end_row end_col]'.\n"
            "For instance, if you want to find the word 'HELLO' starting at row 1, column 1 and ending at row 1, column 5, enter '[1 1 1 5]'.\n"
            "\nGuidelines:\n"
            "- Each guess must be unique; you cannot repeat the same guess.\n"
            "- You have a total of 20 incorrect attempts remaining.\n"
            "- The history of your attempts will be recorded below.\n\n"
            "Make your guesses carefully and strategically. Good luck, Player {player_id}! Let's see how many words you can find!\n"
        )
    
    def _observe_current_state(self) -> None:
        message=f"Current Board:\n\n{self._render_board(self.state.game_state['board'], show_words=True)}\nPlaced Words: {', '.join(self.placed_words.keys())}\nIncorrect Attempts Remaining: {self.num_incorrect_tries}",
        self.state.add_observation(message=message, observation_type=ta.ObservationType.GAME_BOARD)
    
    def _generate_word_search(self):
        ## sample the words
        self.words = random.sample(self.word_list, self.num_words)
        self.words = [word.upper() for word in self.words]
        self.words = sorted(self.words, key=lambda w: len(w), reverse=True)
        self.directions = {word: random.choice(["across", "down"]) for word in self.words}

        self.highlighted_positions = set()
        self.correct_words = set()
        self.incorrect_attempts = []

        grid_size = self._determine_initial_grid_size(self.words)
        grid = self._create_empty_grid(grid_size)

        self.placed_words = {}  # word: (row, col), where 0 is the starting index

        for word in self.words:
            placed = False
            if not self.placed_words:  # First word
                # Place the first word in the center of the grid
                if self.directions[word] == "across":
                    row = grid_size // 2
                    col = (grid_size - len(word)) // 2
                else:
                    row = (grid_size - len(word)) // 2
                    col = grid_size // 2

                if self._can_place_word(grid, word, self.directions[word], row, col):
                    self._place_word_on_grid(grid, word, self.directions[word], row, col)
                    self.placed_words[word] = (row, col, self.directions[word])
                    placed = True
            
            else:
                # Attempt to find overlaps
                possible_positions = self._find_overlaps(word, grid, self.directions)
                random.shuffle(possible_positions)  # Randomize to add variability
                for pos in possible_positions:
                    row, col, direction = pos
                    if self._can_place_word(grid, word, direction, row, col):
                        self._place_word_on_grid(grid, word, direction, row, col)
                        self.placed_words[word] = (row, col, direction)
                        placed = True
                        break

            if not placed:
                # If no overlap placement is possible, try placing the word in any free position
                for row in range(grid_size):
                    for col in range(grid_size):
                        if self._can_place_word(grid, word, self.directions[word], row, col):
                            self._place_word_on_grid(grid, word, self.directions[word], row, col)
                            self.placed_words[word] = (row, col, self.directions[word])
                            placed = True
                            break
                    if placed:
                        break

        # Fill the remaining grid with random letters
        self._fill_empty_cells(grid)
        return grid, self.placed_words

    def _determine_initial_grid_size(self, words):  return round(max(len(word) for word in words) * 1.5)  # Ensures that the grid size is larger than the longest word to allow placement
    def _create_empty_grid(self, size):             return [["." for _ in range(size)] for _ in range(size)]
    def _can_place_word(self, grid, word, direction, row, col):
        if direction == "across":
            if col + len(word) > len(grid[0]):
                return False
            for i, letter in enumerate(word):
                current_cell = grid[row][col + i]
                if current_cell != "." and current_cell != letter: 
                    return False
        else:  # "down"
            if row + len(word) > len(grid):
                return False
            for i, letter in enumerate(word):
                current_cell = grid[row + i][col]
                if current_cell != "." and current_cell != letter:
                    return False

        return True

    def _place_word_on_grid(self, grid, word, direction, row, col):
        if direction == "across":
            for i, letter in enumerate(word):
                grid[row][col + i] = letter
        else:  # "down"
            for i, letter in enumerate(word):
                grid[row + i][col] = letter

    def _find_overlaps(self, word, grid, directions):
        overlaps = []
        for placed_word, (p_row, p_col, p_direction) in self.placed_words.items():
            for i, letter in enumerate(word):
                for j, placed_letter in enumerate(placed_word):
                    if letter == placed_letter:
                        # Determine the possible position based on the direction of the placed word
                        if p_direction == 'across':
                            row = p_row - i
                            col = p_col + j
                            if directions[word] == 'down' and 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                                if self._can_place_word(grid, word, 'down', row, col):
                                    overlaps.append((row, col, 'down'))
                        elif p_direction == 'down':
                            row = p_row + j
                            col = p_col - i
                            if directions[word] == 'across' and 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                                if self._can_place_word(grid, word, 'across', row, col):
                                    overlaps.append((row, col, 'across'))
        return overlaps

    def _fill_empty_cells(self, grid):
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == ".":
                    grid[row][col] = random.choice(string.ascii_uppercase)

    def _validate_and_replace_unintended_words(self, grid, words):
        grid_size = len(grid)
        word_set = set(words)

        # Check each row for unintended words
        for row_index, row in enumerate(grid):
            row_str = "".join(row)
            self._find_and_replace_unintended_words(grid, row_str, word_set, row_index, is_row=True)

        # Check each column for unintended words
        for col_index in range(grid_size):
            col_str = "".join(grid[row][col_index] for row in range(grid_size))
            self._find_and_replace_unintended_words(grid, col_str, word_set, col_index, is_row=False)

    def _find_and_replace_unintended_words(self, grid, string, word_set, index, is_row):
        min_word_length = 3  # Only consider words of length 3 or greater
        placed_positions = self._get_positions()

        for start in range(len(string)):
            for end in range(start + min_word_length, len(string) + 1):
                substring = string[start:end]
                
                # Map the substring positions to (row, col) based on whether it's a row or column
                if is_row:  substring_positions = {(index, start + i) for i in range(len(substring))}
                else:       substring_positions = {(start + i, index) for i in range(len(substring))}
                # Check if any part of the substring overlaps with placed word positions
                if substring_positions & placed_positions: continue  # Skip if any part of the substring overlaps with placed words
                if substring in word_set: continue  # This is an intended word, skip it
                # Check if the substring is a valid English word
                if self._is_valid_word(substring):
                    # print(f"Unintended word found: {substring}")
                    self._replace_unintended_word(grid, substring_positions)

    def _replace_unintended_word(self, grid, positions):
        for row, col in positions: grid[row][col] = random.choice(string.ascii_uppercase)

    def _is_valid_word(self, word):
        return word.lower() in words.words("en")
    
    def _get_positions(self):
        positions = set()
        for word, (row, col, direction) in self.placed_words.items():
            if direction == "across":
                for position in [(row, col + i) for i in range(len(word))]:
                    positions.add(position)
            else:  # "down"
                for position in [(row + i, col) for i in range(len(word))]:
                    positions.add(position)
        return positions
    

    def _render_board(self, grid, show_words=True):
        header = "   " + " ".join(f"C{i:02}" for i in range(len(grid)))
        lines = [header]
        for i, row in enumerate(grid):
            row_str = f"R{i:02} "
            for j, val in enumerate(row):
                if (i, j) in self.highlighted_positions:
                    row_str += f"[{val}] " if show_words else f" {val}  "
                else:
                    row_str += f" {val}  "
            lines.append(row_str)

        return "\n".join(lines)

    def _check_word(self, grid, start_row, start_col, end_row, end_col):
        for placed_word, (row, col, direction) in self.placed_words.items():
            expected_start = (row, col)
            if direction == "across":   expected_end = (row, col + len(placed_word) - 1)
            else:                       expected_end = (row + len(placed_word) - 1, col) # "down"
            actual_start = (start_row, start_col)
            actual_end = (end_row, end_col)
            if (actual_start == expected_start and actual_end == expected_end) or \
            (actual_start == expected_end and actual_end == expected_start):
                self.correct_words.add(placed_word)
                self._highlight_word(start_row, start_col, end_row, end_col)
                # print(f"Correct! The word '{placed_word}' was found.")
                return True

        # If no match, record as an incorrect attempt
        self.incorrect_attempts.append((start_row, start_col, end_row, end_col))
        # print("Incorrect attempt.")
        return False
        
    def _highlight_word(self, start_row, start_col, end_row, end_col):
        if start_row == end_row:  # Horizontal word
            for col in range(min(start_col, end_col), max(start_col, end_col) + 1): self.highlighted_positions.add((start_row, col))
        elif start_col == end_col:  # Vertical word
            for row in range(min(start_row, end_row), max(start_row, end_row) + 1): self.highlighted_positions.add((row, start_col))
        else: print("Invalid input: Words can only be horizontal or vertical.")

    def _extract_word(self, grid, start_row, start_col, end_row, end_col):
        if start_row == end_row:    return "".join(grid[start_row][col] for col in range(min(start_col, end_col), max(start_col, end_col) + 1)) # Horizontal word
        elif start_col == end_col:  return "".join(grid[row][start_col] for row in range(min(start_row, end_row), max(start_row, end_row) + 1)) # Vertical word
        else:                       return ""

    def _matches_position(self, word, row, col, direction, start_row, start_col, end_row, end_col):
        if direction == "across" and row == start_row and col == min(start_col, end_col):   return len(word) == abs(end_col - start_col) + 1
        elif direction == "down" and col == start_col and row == min(start_row, end_row):   return len(word) == abs(end_row - start_row) + 1
        return False
    
    def step(self, action: str) -> Tuple[bool, ta.Info]:
        player_id = self.state.current_player_id
        self.state.add_observation(from_id=player_id, to_id=-1, message=action, observation_type=ta.ObservationType.PLAYER_ACTION) ## Update the observations that was provided by the player
        action_search_pattern = re.compile(r"\[(\d+)\s(\d+)\s(\d+)\s(\d+)\]")
        matches = action_search_pattern.findall(action)
        matches = set(matches)

        if not matches:
            self.state.set_invalid_move(reward=self._get_percentage_completion(), reason=f"Invalid move format. Player {player_id} did not respond with valid 'start_row, start_col, end_row, end_col'.")
        else:
            for match in matches:
                start_row, start_col, end_row, end_col = [int(x) for x in match]
                if not (0 <= start_row < len(self.state.game_state["board"]) 
                        and 0 <= start_col < len(self.state.game_state["board"][0]) 
                        and 0 <= end_row < len(self.state.game_state["board"]) 
                        and 0 <= end_col < len(self.state.game_state["board"][0])):
                    ## action out of bounds
                    self.state.set_invalid_move(reward=self._get_percentage_completion(), reason=f"Invalid move format. Player {player_id} did not respond with valid 'start_row, start_col, end_row, end_col'.")
                    break
                elif (start_row, start_col, end_row, end_col) in self.incorrect_attempts:
                    ## action already attempted
                    self.state.set_invalid_move(reward=self._get_percentage_completion(), reason=f"Invalid move. The action has already been attempted.")
                    break
                elif not self._check_word(self.state.game_state["board"], start_row, start_col, end_row, end_col):
                    ## action is incorrect
                    self.num_incorrect_tries -= 1
                    message=f"[{start_row} {start_col} {end_row} {end_col}] is an incorrect attempt. {self.num_incorrect_tries} incorrect tries remaining."
                    self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=message, observation_type=ta.ObservationType.GAME_MESSAGE)
                    if self.num_incorrect_tries == 0:
                        reward = round(len(self.correct_words) / len(self.placed_words), 3)
                        self.state.set_outcome(reward=reward, reason=f"No more incorrect tries remaining. You found {len(self.correct_words)} out of {len(self.placed_words)} words ({round(reward * 100)}%).")
                    break
                else:
                    ## action is correct
                    word_found = self._map_coordinate_to_word(start_row, start_col, end_row, end_col)
                    if word_found:
                        self.correct_words.add(word_found)
                        self._highlight_word(start_row, start_col, end_row, end_col)
                        message = f"[{start_row} {start_col} {end_row} {end_col}] is a correct attempt. You found the word '{word_found}'."
                    else:
                        message = f"[{start_row} {start_col} {end_row} {end_col}] is a correct attempt, but the word was not found in the placed words."
                    self.state.add_observation(from_id=ta.GAME_ID, to_id=player_id, message=message, observation_type=ta.ObservationType.GAME_MESSAGE)
            
            ## update the game board
            self.state.game_state["rendered_board"] = self._render_board(self.state.game_state["board"], show_words=True)

        if len(self.correct_words) == len(self.placed_words):
            reason = f"Congratulations! You completed the Word Search puzzle."
            self.state.set_outcome(reward=1.0, reason=reason)

        self._observe_current_state()  # Update the current state observation
        return self.state.step()

    def _map_coordinate_to_word(self, start_row: int, start_col: int, end_row: int, end_col: int) -> Union[str, None]:
        for word, (row, col, direction) in self.placed_words.items():
            if self._matches_position(word, row, col, direction, start_row, start_col, end_row, end_col): return word
        return None

    def _get_percentage_completion(self) -> float:
        if not self.placed_words: return 0.0
        return len(self.correct_words) / len(self.placed_words)