"""Test suite for phlmp_cyclingpool."""
# =============================================================================
#                                   TEST PLAN
# -----------------------------------------------------------------------------
# Here we detail the things we are concerned to test and specify which tests
# cover those concerns.
#
# Concerns:
# [ A] _Pool finishes all jobs added to it
# [ A] _Pool returns correct results for the job indices
# [ A] _Pool has nonzero workers before finishing work
# [ A] _Pool has zero workers after finishing work
# [ B] _PoolList workers are all active before yielding results
# [ B] _PoolList returns correct results for the job indices
# [ B] _PoolList has zero active workers after finishing work
# [ B] _Pool finishes all jobs added to it
# [ C] overrun when jobs not finished but conditions are right
# [ C] don't overrun when condition is true but too many active
# [ C] don't overrun when condition is false and not finished
# [ C] overrun when jobs are finished
# [ C] don't overrun when overrunable jobs is zero and unfinished
# [ D] no overrunning if num_jobs is 1
# [ D] no overrunning if there's only 1 worker
# [ D] allow at least one job to overrun if conditions are right
# [ E] CyclingPool has zero active jobs before starting work
# [ E] CyclingPool returns correct results for the job indices
# [ E] CyclingPool has zero active jobs after finishing work
# [ E] CyclingPool finishes all jobs added to it
# [ F] CyclingPool reports active jobs when blocked jobs overrun
# [ F] CyclingPool returns all available results when overrunning
# [ F] CyclingPool returns correct results for overrun job indices
# [ F] CyclingPool reports no active jobs after 'finish_results'
# [ F] CyclingPool finishes all overrun jobs
# [ G] CyclingPool uses current state of jobs in _cycle_results
# [ G] CyclingPool gets results of all jobs when cycling
# [ H] CyclingPool processes all jobs at least once when overrunning
# [ H] CyclingPool does not duplicate overrun jobs
# [ H] CyclingPool reports active overrunning jobs
# -----------------------------------------------------------------------------
# Tests:
# [ A] test_A_pool_breathing
# [ B] test_B_poollist_breathing
# [ C] test_C_calc_should_overrun
# [ D] test_D_calc_overrunnable_workers
# [ E] test_E_cyclingpool_breathing
# [ F] test_F_can_overrun
# [ G] test_G_can_cycle
# [ H] test_H_can_overrun_cycle
# =============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import multiprocessing
import unittest

import phlmp_cyclingpool


class _TestJob(object):

    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value


class _LockedJob(object):

    def __init__(self, value, lock):
        self.value = value
        self.lock = lock

    def __call__(self):
        with self.lock:
            return self.value


def _false_condition():
    return False


def _true_condition():
    return True


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_A_pool_breathing(self):

        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        max_workers = multiprocessing.cpu_count()

        pool = phlmp_cyclingpool._Pool(job_list, max_workers)

        # [ A] _Pool has nonzero workers before finishing work
        self.assertTrue(pool.count_active_workers() > 0)

        for i in input_list:
            pool.add_job_index(i)
        pool.finish()

        result_list = []

        while not pool.is_finished():
            pool.join_finished_workers()
            for index, result in pool.yield_available_results():
                # [ A] _Pool returns correct results for the job indices
                self.assertEqual(index, result)
                result_list.append(result)

        # [ A] _Pool has zero workers after finishing work
        self.assertEqual(pool.count_active_workers(), 0)

        # [ A] _Pool finishes all jobs added to it
        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_B_poollist_breathing(self):

        max_workers = multiprocessing.cpu_count()
        input_list = list(xrange(max_workers))
        job_list = [_TestJob(i) for i in input_list]

        pool_list = phlmp_cyclingpool._PoolList()

        pool = phlmp_cyclingpool._Pool(job_list, max_workers)
        for i in input_list:
            pool.add_job_index(i)
        pool.finish()

        pool_list.add_pool(pool)

        # [ B] _PoolList workers are all active before yielding results
        self.assertEqual(
            pool_list.count_active_workers(),
            max_workers)

        result_list = []
        while not pool_list.is_yield_finished():
            for index, result in pool_list.yield_available_results():
                # [ B] _PoolList returns correct results for the job indices
                self.assertEqual(index, result)
                result_list.append(result)

        # [ B] _PoolList has zero active workers after finishing work
        self.assertFalse(pool_list.count_active_workers())

        # [ B] _Pool finishes all jobs added to it
        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_C_calc_should_overrun(self):

        fcond = _false_condition
        tcond = _true_condition

        expectations = (

            # [ C] overrun when jobs not finished but conditions are right
            ({'active': 0, 'over': 1, 'cond': tcond, 'is_fin': False}, True),
            ({'active': 1, 'over': 1, 'cond': tcond, 'is_fin': False}, True),

            # [ C] don't overrun when condition is true but too many active
            ({'active': 2, 'over': 1, 'cond': tcond, 'is_fin': False}, False),

            # [ C] don't overrun when condition is false and not finished
            ({'active': 0, 'over': 1, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 1, 'over': 1, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 2, 'over': 1, 'cond': fcond, 'is_fin': False}, False),

            # [ C] continue when jobs are finished
            ({'active': 0, 'over': 1, 'cond': tcond, 'is_fin': True}, True),
            ({'active': 0, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            # these shouldn't happen, but test anyway
            ({'active': 1, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            ({'active': 1, 'over': 1, 'cond': tcond, 'is_fin': True}, True),
            ({'active': 2, 'over': 1, 'cond': fcond, 'is_fin': True}, True),
            ({'active': 2, 'over': 1, 'cond': tcond, 'is_fin': True}, True),

            # [ C] don't overrun when overrunable jobs is zero and unfinished
            ({'active': 0, 'over': 0, 'cond': fcond, 'is_fin': False}, False),
            ({'active': 1, 'over': 0, 'cond': tcond, 'is_fin': False}, False),
        )

        for e in expectations:
            args = e[0]
            print(args)
            self.assertEqual(
                phlmp_cyclingpool._calc_should_overrun(
                    num_active=args['active'],
                    num_overrunnable=args['over'],
                    condition=args['cond'],
                    is_finished=args['is_fin']),
                e[1])

    def test_D_calc_overrunnable_workers(self):

        expectations = (
            # [ D] no overrunning if num_jobs is 1
            ({'max_workers': 1, 'max_overrunnable': 1, 'num_jobs': 1}, 0),
            ({'max_workers': 1, 'max_overrunnable': 2, 'num_jobs': 1}, 0),
            ({'max_workers': 2, 'max_overrunnable': 1, 'num_jobs': 1}, 0),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 1}, 0),

            # [ D] no overrunning if there's only 1 worker
            ({'max_workers': 1, 'max_overrunnable': 1, 'num_jobs': 2}, 0),
            ({'max_workers': 1, 'max_overrunnable': 2, 'num_jobs': 2}, 0),

            # [ D] allow at least one job to overrun if conditions are right
            ({'max_workers': 2, 'max_overrunnable': 1, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 2, 'num_jobs': 3}, 1),
            ({'max_workers': 2, 'max_overrunnable': 3, 'num_jobs': 2}, 1),
            ({'max_workers': 2, 'max_overrunnable': 3, 'num_jobs': 3}, 1),
            ({'max_workers': 3, 'max_overrunnable': 2, 'num_jobs': 2}, 1),
            ({'max_workers': 3, 'max_overrunnable': 2, 'num_jobs': 3}, 2),
            ({'max_workers': 3, 'max_overrunnable': 3, 'num_jobs': 2}, 1),
            ({'max_workers': 3, 'max_overrunnable': 3, 'num_jobs': 3}, 2),
        )

        for e in expectations:
            print(e[0])

            # PyChecker makes us do this because it doesn't see the **e[0] as
            # passing all the required parameters
            calc_overrun = phlmp_cyclingpool._calc_overrunnable_workers

            self.assertEqual(
                calc_overrun(**e[0]),
                e[1])

    def test_E_cyclingpool_breathing(self):

        input_list = list(xrange(100))
        job_list = [_TestJob(i) for i in input_list]
        result_list = []
        max_workers = multiprocessing.cpu_count()
        max_overrunnable = max_workers // 2
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        # [ E] CyclingPool has zero active jobs before starting work
        self.assertEqual(pool.num_active_jobs, 0)

        for index, result in pool._cycle_results(_false_condition):
            # [ E] CyclingPool returns correct results for the job indices
            self.assertEqual(index, result)
            result_list.append(result)

        # [ E] CyclingPool has zero active jobs after finishing work
        self.assertEqual(pool.num_active_jobs, 0)

        # [ E] CyclingPool finishes all jobs added to it
        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_F_can_overrun(self):

        lock = multiprocessing.Lock()

        max_workers = 10
        max_overrunnable = max_workers // 2
        half_max_workers = max_workers // 2
        input_list = list(xrange(max_workers))
        block_input_list = input_list[:half_max_workers]
        normal_input_list = input_list[half_max_workers:]
        self.assertTrue(len(normal_input_list) >= len(block_input_list))

        block_job_list = [_LockedJob(i, lock) for i in block_input_list]
        normal_job_list = [_TestJob(i) for i in normal_input_list]
        job_list = block_job_list + normal_job_list

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        # Acquire lock before starting cycle, to ensure that 'block_job_list'
        # jobs won't complete. This will force the pool to overrun those jobs.
        with lock:
            for index, result in pool._cycle_results(_true_condition):
                self.assertEqual(index, result)
                result_list.append(result)

            # [ F] CyclingPool reports active jobs when blocked jobs overrun
            self.assertEqual(pool.num_active_jobs, max_overrunnable)

        # [ F] CyclingPool returns all available results when overrunning
        # make sure that all the normal jobs were processed and none of the
        # blocked jobs were processed
        self.assertSetEqual(
            set(result_list),
            set(normal_input_list))

        # finish all remaining jobs
        for index, result in pool.finish_results():
            # [ F] CyclingPool returns correct results for overrun job indices
            self.assertEqual(index, result)
            result_list.append(result)

        # [ F] CyclingPool reports no active jobs after 'finish_results'
        self.assertEqual(pool.num_active_jobs, 0)

        # [ F] CyclingPool finishes all overrun jobs
        # assert that all jobs have been processed
        self.assertSetEqual(
            set(result_list),
            set(input_list))

    def test_G_can_cycle(self):

        num_loops = 2
        num_jobs = 100
        input_list = list(xrange(num_jobs))
        job_list = [_TestJob(i) for i in input_list]
        max_workers = multiprocessing.cpu_count()
        max_overrunnable = max_workers // 2
        print("max workers:", max_workers)

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        for i in xrange(num_loops):

            loop_offset = i * num_jobs

            for index, result in pool._cycle_results(_false_condition):
                # [ G] CyclingPool uses current state of jobs in _cycle_results
                self.assertEqual(index + loop_offset, result)
                result_list.append(result)

            # [ G] CyclingPool gets results of all jobs when cycling
            self.assertSetEqual(
                set(result_list),
                set(xrange(num_jobs + loop_offset)))

            # ensure the next batch of jobs continue the numbering at the next
            # loop offset
            for job in job_list:
                job.value += num_jobs

    def test_H_can_overrun_cycle(self):
        # suppress pychecker error on collections.Counter:
        # Methods (fromkeys) in collections.Counter need to be overridden in a
        # subclass
        __pychecker__ = 'no-abstract'  # NOQA

        max_workers = 10
        max_overrunnable = max_workers // 2
        half_max_workers = max_workers // 2
        num_loops = half_max_workers
        num_jobs = max_workers

        locks = [multiprocessing.Lock() for _ in xrange(half_max_workers)]

        input_list = list(xrange(num_jobs))

        block_input_list = input_list[:half_max_workers]
        normal_input_list = input_list[half_max_workers:]

        self.assertTrue(len(normal_input_list) >= len(block_input_list))

        block_job_list = [
            _LockedJob((0, i), locks[i])
            for i in block_input_list
        ]
        normal_job_list = [_TestJob((0, i)) for i in normal_input_list]
        job_list = block_job_list + normal_job_list

        result_list = self._loop_jobs(
            max_workers, num_loops, locks, max_overrunnable, job_list)

        # count iterations of each job
        job_counter = collections.Counter()
        for result in result_list:
            iteration, job_index = result
            job_counter[job_index] += 1

        # [ H] CyclingPool processes all jobs at least once when overrunning
        for i in input_list:
            self.assertTrue(job_counter[i] >= 1)

        # [ H] CyclingPool does not duplicate overrun jobs
        # assert that blocked jobs were processed at most the number of cycles
        # until they were blocked
        for i in block_input_list:
            self.assertTrue(job_counter[i] <= i + 1)

    def _loop_jobs(
            self, max_workers, num_loops, locks, max_overrunnable, job_list):

        num_jobs = len(job_list)

        result_list = []
        pool = phlmp_cyclingpool.CyclingPool(
            job_list, max_workers, max_overrunnable)

        print("max workers:", max_workers)

        result_list = []
        for i in xrange(num_loops):

            # Acquire lock before starting cycle, to ensure that some of the
            # 'block_job_list' jobs won't complete. This will force the pool to
            # overrun those jobs.
            locks[i].acquire()

            loop_offset = i * num_jobs

            for index, result in pool._cycle_results(_true_condition):
                iteration, job_index = result
                self.assertEqual(index, job_index)
                result_list.append(result)

            # make sure that some of the jobs weren't processed yet
            self.assertTrue(
                len(set(result_list)) < loop_offset + num_jobs)

            # [ H] CyclingPool reports active overrunning jobs
            # make sure that some jobs are still running
            self.assertTrue(pool.num_active_jobs)

            # mark subsequent jobs as coming from the next iteration
            for job in job_list:
                iteration, job_index = job.value
                job.value = (iteration + 1, job_index)

        # finish all remaining jobs
        for l in locks:
            l.release()
        for index, result in pool.finish_results():
            result_list.append(result)

        # assert no jobs left
        self.assertFalse(pool.num_active_jobs)

        return result_list


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
