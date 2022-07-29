from tqdm import tqdm
import pandas as pd
from itertools import combinations
import logging

logging.basicConfig(level=logging.INFO)


class KWGenerator(object):

    """class to generate seed letters from csv noun list"""

    def __init__(self, nounlist_path, nationcode="en"):

        self.noundf = self.read_nounlist(nounlist_path)
        self.nationcode = nationcode
        if nationcode == "en":
            self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        elif nationcode == "de":
            self.alphabet = "abcdefghijklmnopqrstuvwxyzäöüß"

    def read_nounlist(self, nounlist_path):
        """read nounlist to daraframe"""

        df = pd.read_csv(nounlist_path, on_bad_lines="skip")
        df.columns.values[0] = "noun"
        df["noun"] = df["noun"].str.lower()

        return df

    def dist_of_combiletters(self, letterlist):

        """function to create distribution of letters from alphabet

        Parameters
        ----------
        letterlist: list of combi letter to concatenate with letters from alphabet

        Returns
        -------
        dictionary: dictionary of letter distribution
        """
        dic = {}
        # combine a letter of each letter list A (abcd...) to another letter list ( abcd...) to (aa,ab,ac,ad,ba,bb...), which are keys of a dictionary
        # dictionary value are occurrences of these letters in the nounlist
        for _1st_let in tqdm(letterlist):
            for _2nd_let in self.alphabet:
                dic[f"{_1st_let}{_2nd_let}"] = len(
                    self.noundf[
                        self.noundf["noun"].str.startswith(f"{_1st_let}{_2nd_let}")
                    ]
                )

        return dic

    def create_seeds_file(self):
        """function to create seed file from noun list"""

        combif2letters = combinations(self.alphabet, 2)
        liof2letters = ["".join(i) for i in combif2letters]
        print(len(liof2letters))
        pd.Series(liof2letters).to_csv(
            f"./data/{self.nationcode}/{self.nationcode}_2letters.csv",
            index=False,
            header=None,
        )

        dic2 = self.dist_of_combiletters(self.alphabet)
        li2 = [key for key in dic2 if dic2[key] >= 1]

        dicf3letters = self.dist_of_combiletters(li2)
        liof3letters = [key for key in dicf3letters if dicf3letters[key] >= 1]
        print(len(liof3letters))
        pd.Series(liof3letters).to_csv(
            f"./data/{self.nationcode}/{self.nationcode}_3letters.csv",
            index=False,
            header=None,
        )

        dicf4letters = self.dist_of_combiletters(liof3letters)
        liof4letters = [key for key in dicf4letters if dicf4letters[key] >= 1]
        print(len(liof4letters))
        pd.Series(liof4letters).to_csv(
            f"./data/{self.nationcode}/{self.nationcode}_4letters.csv",
            index=False,
            header=None,
        )
