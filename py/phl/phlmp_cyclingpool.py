"""Distribute jobs across multiple processes."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# phlmp_cyclingpool
#
# Public Classes:
#   CyclingPool
#    .cycle_results
#    .finish_results
#    .num_active_jobs
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import multiprocessing
import multiprocessing.queues

import phlsys_timer


class CyclingPool(object):

    """Pooling for jobs that are repeated in a loop, supports overruning jobs.

    This is useful if you have a lot of polling jobs which usually don't
    need to do much work. When they occasionally do need to do a lot of
    work, you don't want to stop cycling the other jobs while they're
    processed.

    Jobs are processed in separate worker processes, this means that changes to
    the jobs or any global state will not be reflected in the calling process.

    Jobs started during each 'cycle_results' are guaranteed to be handled in
    new forks of the current process. This means that the current version of
    the jobs in the supplied job list will be used.

    """

    def __init__(self, job_list, max_workers, max_overrunnable):
        """Create a CyclingPool to cycle over 'job_list'.

        :job_list: a list of callables to execute in worker processes
        :max_workers: the maximum number of worker processes to make
        :max_overrunnable: the maximum number of workers to leave behind

        """
        super(CyclingPool, self).__init__()

        if max_workers < 1:
            raise ValueError(
                'invalid value for max_workers: {}'.format(max_workers))

        if max_overrunnable < 0:
            raise ValueError(
                'invalid value for max_overrunnable: {}'.format(
                    max_overrunnable))

        if max_overrunnable >= max_workers:
            raise ValueError(
                'invalid value for max_overrunnable: {}, should be less '
                'than max_workers: {}'.format(
                    max_overrunnable, max_workers))

        self._job_list = job_list
        self._max_workers = max_workers
        self._overunnable_workers = _calc_overrunnable_workers(
            max_workers=max_workers,
            max_overrunnable=max_overrunnable,
            num_jobs=len(job_list))
        self._pool_list = _PoolList()
        self._active_job_index_set = set()

    def cycle_results(self, overrun_secs):
        """Yield the results from a run of all the jobs.

        If overrun_secs elapse and max_overrunnable is nonzero then jobs may be
        left to run in the background.

        The results from these 'overrun' jobs will be yielded in subsequent
        calls to 'cycle_results' or 'finish_results'.

        Jobs which are currently overrunning will not be started again until
        the overrun job has finished.

        :overrun_secs: seconds to wait before considering leaving jobs behind
        :yields: an (index, result) tuple

        """

        # make a timer out of the overrun_secs and pass to _cycle_results
        timer = phlsys_timer.Timer()
        timer.start()

        def overrun_condition():
            return timer.duration >= overrun_secs

        for index, result in self._cycle_results(overrun_condition):
            yield index, result

    def finish_results(self):
        """Yield the results from any outstanding jobs, block until done."""
        while not self._pool_list.is_yield_finished():
            for index, result in self._overrun_cycle_results():
                yield index, result

    @property
    def num_active_jobs(self):
        """Return the number of jobs not yet yielded."""
        return len(self._active_job_index_set)

    def _overrun_cycle_results(self):
        for index, result in self._pool_list.yield_available_results():
            self._active_job_index_set.remove(index)
            yield index, result

    def _cycle_results(self, overrun_condition):

        # clear up any dead pools and yield results
        for i, res in self._overrun_cycle_results():
            yield i, res

        self._start_new_cycle()

        # wait for results, overrun if half our workers are available
        should_break = False
        while not should_break:

            should_break = _calc_should_overrun(
                num_active=self._pool_list.count_active_workers(),
                num_overrunnable=self._overunnable_workers,
                condition=overrun_condition,
                is_finished=self._pool_list.is_yield_finished())

            for index, result in self._overrun_cycle_results():
                yield index, result

    def _start_new_cycle(self):

        active_workers = self._pool_list.count_active_workers()
        max_new_workers = self._max_workers - active_workers

        pool = _Pool(self._job_list, max_new_workers)

        # schedule currently inactive jobs in the new pool
        all_job_index_set = set(xrange(len(self._job_list)))
        inactive_job_index_set = all_job_index_set - self._active_job_index_set
        for i in inactive_job_index_set:
            pool.add_job_index(i)
            self._active_job_index_set.add(i)
        pool.finish()

        self._pool_list.add_pool(pool)


def _calc_overrunnable_workers(max_workers, max_overrunnable, num_jobs):
    return min(
        max_workers - 1,
        num_jobs - 1,
        max_overrunnable)


def _calc_should_overrun(num_active, num_overrunnable, condition, is_finished):
    too_busy = num_active > num_overrunnable
    can_overrun = not too_busy and condition()
    return is_finished or can_overrun


class _PoolList(object):

    def __init__(self):
        self._pool_list = []

    def add_pool(self, pool):
        self._pool_list.append(pool)

    def count_active_workers(self):
        active_workers = 0
        for pool in self._pool_list:
            active_workers += pool.count_active_workers()
        return active_workers

    def yield_available_results(self):

        # yield results
        for pool in self._pool_list:
            pool.join_finished_workers()
            for index, result in pool.yield_available_results():
                yield index, result

        # clean up dead pools
        finished_pools = []
        for pool in self._pool_list:
            if pool.is_finished():
                finished_pools.append(pool)
        for pool in finished_pools:
            self._pool_list.remove(pool)

    def is_yield_finished(self):
        return not self._pool_list


class _Pool(object):

    def __init__(self, job_list, max_workers):
        super(_Pool, self).__init__()

        if max_workers < 1:
            raise ValueError(
                'invalid value for max_workers: {}'.format(max_workers))

        # pychecker makes us do this, it won't recognise that
        # multiprocessing.queues is a thing.
        mp = multiprocessing
        self._job_index_queue = mp.queues.SimpleQueue()
        self._results_queue = mp.queues.SimpleQueue()

        # create the workers
        self._worker_list = []
        num_workers = min(max_workers, len(job_list))
        for _ in xrange(num_workers):
            worker = multiprocessing.Process(
                target=_worker_process,
                args=(job_list, self._job_index_queue, self._results_queue))
            worker.start()
            self._worker_list.append(worker)

    def add_job_index(self, job_index):
        self._job_index_queue.put(job_index)

    def finish(self):
        # the worker processes will stop when they process 'None'
        for _ in xrange(len(self._worker_list)):
            self._job_index_queue.put(None)

    def join_finished_workers(self):

        # join all finished workers and remove from list
        finished_workers = []
        for worker in self._worker_list:
            if not worker.is_alive():
                worker.join()
                finished_workers.append(worker)
        for worker in finished_workers:
            self._worker_list.remove(worker)

    def yield_available_results(self):
        while not self._results_queue.empty():
            yield self._results_queue.get()

    def count_active_workers(self):
        return len(self._worker_list)

    def is_finished(self):
        return not self._worker_list


def _worker_process(job_list, work_queue, results_queue):
    while True:
        job_index = work_queue.get()
        if job_index is None:
            break
        job = job_list[job_index]
        results = job()
        results_queue.put((job_index, results))


# -----------------------------------------------------------------------------
# Copyright (C) 2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
