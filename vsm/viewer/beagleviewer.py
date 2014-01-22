import numpy as np

from vsm.linalg import row_norms as _row_norms_
from vsm.linalg import (
    row_acos as _row_acos_,
    row_acos_mat as _row_acos_mat_)

from similarity import (
    sim_word_word as _sim_word_word_,
    simmat_words as _simmat_words_)

from plotting import (
    gen_colors as _gen_colors_,
    plot_clusters as _plot_clusters_)


class BeagleViewer(object):
    """
    A class for viewing BEAGLE models.

    :param corpus: Source of observed data.
    :type corpus: Corpus
    
    :param model: One of the Beagle objects.
    :type model: Beagle object

    :attributes:
        * **corpus** (Corpus object) - `corpus`
        * **model** (Beagle object) - `model`

    :methods:
        * :doc:`beagle_sim_word_word`
            Returns words sorted by the cosine similarity values between
            word(s) and every word.
        * :doc:`beagle_simmat_words`
            Calculates the similarity matrix for a given list of words.
        * :doc:`beagle_isomap_words`
    """
    def __init__(self, corpus, model):
        """
        """
        self.corpus = corpus
        self.model = model
        self._word_norms_ = None


    @property
    def _word_norms(self):
        """
        """
        if self._word_norms_ is None:
            self._word_norms_ = _row_norms_(self.model.matrix)            

        return self._word_norms_


    def sim_word_word(self, word_or_words, weights=None, 
                      filter_nan=True, print_len=10, as_strings=True,
                      sim_fn=_row_acos_, order='i'):
        """
        A wrapper of `sim_word_word` in similarity.py

        :param word_or_words: Query word(s) to which similarity values are calculated.
        :type word_or_words: string or list of strings
        
        :param weights: Specify weights for each query word in `word_or_words`. 
            Default uses equal weights (i.e. arithmetic mean)
        :type weights: list of floating point, optional
        
        :param filter_nan: If `True` not a number entries are filtered.
            Default is `True`.
        :type filter_nan: boolean, optional

        :param print_len: Number of words printed by pretty-printing function
            Default is 10.
        :type print_len: int, optional

        :param as_strings: If `True`, returns a list of words as strings rather
            than their integer representations. Default is `True`.
        :type as_strings: boolean, optional

        :param sim_fn: A similarity function from functions in vsm.linalg. 
            Default is :meth: row_acos.
        :type sim_fn: string, optional

        :param order: Default is 'i'.
        :type order: string, optional

        :returns: w_arr : :class:`LabeledColumn`.
            A 2-dim array containing words and their cosine values to 
            `word_or_words`. 
        
        :See Also: :meth:`vsm.viewer.similarity.sim_word_word`
        """
        return _sim_word_word_(self.corpus, self.model.matrix, 
                               word_or_words, weights=weights, 
                               norms=self._word_norms, filter_nan=filter_nan, 
                               print_len=print_len, as_strings=True,
                               sim_fn=sim_fn, order=order)


    def simmat_words(self, word_list, sim_fn=_row_acos_mat_):
        """
        Calculates the similarity matrix for a given list of words.

        :param word_list: A list of words whose similarity matrix is to be
            computed.
        :type word_list: list

        :param sim_fn: A similarity function from functions in vsm.linalg. 
            Default is :meth: row_acos_mat.
        :type sim_fn: string, optional

        :returns: :class:`IndexedSymmArray`.
            n x n matrix containing floats where n is the number of words
            in `word_list`.
        
        :See Also: :meth:`vsm.viewer.similarity.simmat_words`
        """
        return _simmat_words_(self.corpus, self.model.matrix,
                              word_list, sim_fn=sim_fn)


    # This is a quick adaptation of the isomap_docs function from
    # ldagibbsviewer. This should be abstracted and moved to
    # similarity.py or something equivalent.
    def isomap_words(self, words=[], weights=None, thres=.8,
                     n_neighbors=5, scale=True, trim=20):
        """
        """
        from sklearn import manifold
        from math import ceil

        # create a list to be plotted
        word_list = self.sim_word_word(words, weights=weights)

        # cut down the list by the threshold
        labels, size = zip(*[(w,s) for (w,s) in word_list if s < thres])
        print size
        # calculate coordinates
        simmat = self.simmat_words(labels)
        simmat = np.clip(simmat, 0, 1)     # cut off values outside [0, 1]
        imap = manifold.Isomap(n_components=2, n_neighbors=n_neighbors)
        pos  = imap.fit(simmat).embedding_

        # set graphic parameters
        # - scale point size
        if scale:
            size = [s+0.5 if s == 0 else s for s in size] # for given word which has 0.0
            # value to be visible.
            size = [s**2*150 for s in size] 
        else:
            size = np.ones_like(size) * 50
        # - trim labels
        if trim:
            labels = [lab[:trim] for lab in labels]

        # hack for unidecode issues in matplotlib
        labels = [label.decode('utf-8', 'ignore') for label in labels]
        
        return _plot_clusters_(pos, labels, size=size)

