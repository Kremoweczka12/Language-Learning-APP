

class StagesOrdering:
    CONFIG_CREATION_STAGES = ["words", "words_sounds", "sentences", "sentences_sounds", "images", "filters_columns"]
    single_choice_creation = [1, 3, 4]
    creation_position = 0
    CONFIG_CREATION_DESCRIPTIONS = [
        "(1/6) Pick columns that represent words (one word can have multiple representations)\n"
        "For example good choice would be columns where such a values occur:\n"
        " 'apple', 'ringo' , 'りんご' they all represent 'apple' in japanese.",
        "(2/6) Pick one column which constains sound files names of words (This functionality is completely optional so you can leave it empty)"
        ,
        "(3/6) Pick columns that represent sentence examples for words,\n it would be good if for sentence to have translation so optimaly you should choose 2 columns \n(This functionality is completely optional so you can left it empty)"
        "example: sentence_1, sentence_1_translation,",
        "(4/6) Pick one column which constains sound files names of sentences\n (This functionality is completely optional so you can leave it empty)",
        "(5/6) Pick one column which constains image files names for words\n (This functionality is completely optional so you can leave it empty)",
        "(6/6) Pick columns that will be used to filter your words in set \npresentation example columns 'difficulty', 'category', 'subcategory' and etc."]


class UFTIcons:
    RIGHT_ARROW = "⇛"


class StyleSheets:
    FALLING_BUTTON_STYLE_SHEET = """
QPushButton {
  padding: 0.6em 1.7em;

  margin: 0 0.3em 0.3em 0;
  border-radius: 0.12em;

    font-size: 26px;
  text-decoration: none;
  font-family: "Roboto", sans-serif;
  font-weight: 400;
  color: #ffffff;
  text-align: center;

}

QPushButton:hover {
  color: #000000;
  background-color: #ffffff;
}

"""

    CORRECT_BUTTON_STYLE_SHEET = """
QPushButton {
  padding: 0.6em 1.7em;

  margin: 0 0.3em 0.3em 0;
  border-radius: 0.12em;

    font-size: 26px;
  text-decoration: none;
  font-family: "Roboto", sans-serif;
  font-weight: 400;
  color: green;
  text-align: center;

}

QPushButton:hover {
  color: white;
  background-color: green;
}

"""
    FALSE_BUTTON_STYLE_SHEET = """
    QPushButton {
      padding: 0.6em 1.7em;

      margin: 0 0.3em 0.3em 0;
      border-radius: 0.12em;

        font-size: 26px;
      text-decoration: none;
      font-family: "Roboto", sans-serif;
      font-weight: 400;
      color: red;
      text-align: center;

    }

    QPushButton:hover {
      color: white;
      background-color: red;
    }

    """

    TASK_BAR_BUTTON_SHEET = """QPushButton {
  padding: 0.6em 1.7em;

  margin: 0 0.3em 0.3em 0;
  border-radius: 0.12em;
  color: #ffffff;
  background-color: #000000;  

  text-decoration: none;
  font-family: "Roboto", sans-serif;
  font-weight: 300;
  color: #ffffff;
  text-align: center;

}

QPushButton:hover {
  color: #000000;
  background-color: #ffffff;
}
"""

    PLAY_WORD_SOUND_BUTTON = """
    QPushButton {
      text-align: left;
      padding: 0.6em 1.7em;

      margin: 0 0.3em 0.3em 0;
      border-radius: 0.12em;

        font-size: 22px;
      text-decoration: none;
      font-family: "Roboto", sans-serif;
      font-weight: 300;
      color: white;

    }

    QPushButton:hover {
      text-align: left;
      color: black;
      background-color: white;
    }

    """