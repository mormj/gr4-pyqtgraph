/* -*- c++ -*- */
/*
 * Copyright 2022 Josh Morman
 *
 * This file is part of GNU Radio
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 */

#pragma once

#include <gnuradio/pyqtgraph/pg_table.h>

namespace gr {
namespace pyqtgraph {

class pg_table_cpu : public virtual pg_table
{
public:
    pg_table_cpu(block_args args);
    virtual work_return_code_t work(std::vector<block_work_input_sptr>& work_input,
                                    std::vector<block_work_output_sptr>& work_output) override;

private:
    // private variables here
};

} // namespace pyqtgraph
} // namespace gr